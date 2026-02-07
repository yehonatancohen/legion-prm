
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Trophy, Home, User, Download, FileSpreadsheet, Loader2, Sparkles, LogOut } from "lucide-react";
import { ProgressTracker } from "@/components/progress-tracker";
import { TodayProgress, VcfBatch } from "@/types/contacts";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";

export default function DashboardPage() {
    const [todayProgress, setTodayProgress] = useState<TodayProgress | null>(null);
    const [batches, setBatches] = useState<VcfBatch[]>([]);
    const [loading, setLoading] = useState(true);
    const [userData, setUserData] = useState<any>(null);
    const router = useRouter();

    const handleLogout = () => {
        localStorage.removeItem("token");
        router.push("/login");
    };

    const fetchData = async () => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login"); // Redirect if not logged in
            return;
        }

        try {
            // Fetch User Data (Dashboard)
            const dashboardRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/agent/dashboard`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // Handle auth errors
            if (dashboardRes.status === 401 || dashboardRes.status === 403) {
                console.error("Auth error - clearing token");
                localStorage.removeItem("token");
                router.push("/login");
                return;
            }

            if (dashboardRes.ok) setUserData(await dashboardRes.json());

            // Fetch Today's Progress
            const progressRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/contacts/agent/progress/today`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (progressRes.ok) setTodayProgress(await progressRes.json());

            // Fetch Batches
            const batchesRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/contacts/agent/vcf/batches`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (batchesRes.ok) {
                const data = await batchesRes.json();
                if (Array.isArray(data)) setBatches(data);
            }

        } catch (error) {
            console.error("Dashboard fetch error:", error);
            toast.error("Failed to load dashboard data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleDownload = async (batchId: string, fileName: string) => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/contacts/agent/vcf/download/${batchId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!res.ok) throw new Error("Download failed");

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName || 'contacts.vcf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            toast.success("VCF Downloaded!");
        } catch (e) {
            toast.error("Could not download file");
        }
    };

    if (loading) return <div className="flex h-screen items-center justify-center"><Loader2 className="animate-spin" /></div>;

    return (
        <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-slate-950 pb-24">

            {/* Header */}
            <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b px-4 py-3 flex items-center justify-between">
                <div>
                    <h1 className="font-bold text-xl">Legion Command</h1>
                    <p className="text-xs text-muted-foreground">{userData?.user?.name || 'Agent'}</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="bg-emerald-500/10 text-emerald-500 px-3 py-1 rounded-full text-sm font-bold border border-emerald-500/20 flex items-center gap-1">
                        <Sparkles size={14} />
                        {userData?.user?.score || 0} XP
                    </div>
                    <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
                        <LogOut className="h-5 w-5 text-muted-foreground" />
                    </Button>
                </div>
            </header>

            <main className="flex-1 p-4 space-y-6">

                {/* Progress Tracker Widget */}
                <ProgressTracker
                    initialProgress={todayProgress}
                    onUpdate={fetchData}
                />

                {/* My Batches Section */}
                <div>
                    <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                        <FileSpreadsheet size={18} />
                        Active Contact Batches
                    </h3>

                    {batches.length === 0 ? (
                        <Card>
                            <CardContent className="pt-6 text-center text-muted-foreground">
                                <p>No batches assigned yet.</p>
                            </CardContent>
                        </Card>
                    ) : (
                        <div className="space-y-3">
                            {batches.map((batch) => (
                                <Card key={batch.id} className="overflow-hidden">
                                    <div className="flex items-center justify-between p-4">
                                        <div>
                                            <h4 className="font-medium text-sm text-muted-foreground">Batch #{batch.start_serial}</h4>
                                            <p className="font-bold text-lg">{batch.contact_count} Contacts</p>
                                            <div className="text-xs bg-secondary inline-block px-2 py-0.5 rounded mt-1">
                                                Prefix: {batch.prefix}
                                            </div>
                                        </div>
                                        <Button
                                            size="icon"
                                            variant="outline"
                                            onClick={() => handleDownload(batch.id, batch.file_name)}
                                        >
                                            <Download size={20} />
                                        </Button>
                                    </div>
                                    <div className="bg-muted/50 px-4 py-2 text-xs text-muted-foreground flex justify-between">
                                        <span>Status: {batch.status}</span>
                                        <span>{new Date(batch.created_at).toLocaleDateString()}</span>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>

            </main>

            {/* Bottom Nav */}
            <nav className="fixed bottom-0 left-0 right-0 bg-background border-t flex justify-around py-3 pb-safe z-20">
                <Link href="/dashboard" className="flex flex-col items-center text-primary gap-1">
                    <Home className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Mission</span>
                </Link>
                <Link href="/leaderboard" className="flex flex-col items-center text-muted-foreground gap-1 hover:text-primary">
                    <Trophy className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Leaderboard</span>
                </Link>
                <Link href="/profile" className="flex flex-col items-center text-muted-foreground gap-1 hover:text-primary">
                    <User className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Profile</span>
                </Link>
            </nav>
        </div>
    );
}
