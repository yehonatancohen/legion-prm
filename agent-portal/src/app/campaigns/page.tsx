"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Trophy, Home, User, Loader2, Link2, ExternalLink, Copy, Check, DollarSign, Eye, Sparkles, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

interface Campaign {
    id: string;
    name: string;
    description: string | null;
    target_url: string;
    payout_per_view: number;
    points_per_view: number;
}

interface TrackingLink {
    short_code: string;
    full_url: string;
    view_count: number;
    unique_view_count: number;
    earnings: number;
}

interface CampaignData {
    campaign: Campaign;
    my_link: TrackingLink | null;
    my_earnings: number;
    my_views: number;
}

export default function CampaignsPage() {
    const [campaigns, setCampaigns] = useState<CampaignData[]>([]);
    const [loading, setLoading] = useState(true);
    const [joiningId, setJoiningId] = useState<string | null>(null);
    const [copiedCode, setCopiedCode] = useState<string | null>(null);
    const router = useRouter();

    const fetchCampaigns = async () => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/campaigns/agent/campaigns`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (res.status === 401 || res.status === 403) {
                localStorage.removeItem("token");
                router.push("/login");
                return;
            }

            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data)) setCampaigns(data);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCampaigns();
    }, []);

    const handleJoin = async (campaignId: string) => {
        setJoiningId(campaignId);
        const token = localStorage.getItem("token");

        try {
            const res = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/campaigns/agent/campaigns/${campaignId}/join`,
                {
                    method: "POST",
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            if (res.ok) {
                const data = await res.json();
                toast.success(`Joined! Your link: ${data.tracking_url}`);
                fetchCampaigns();
            } else {
                const err = await res.json();
                toast.error(err.detail || "Failed to join");
            }
        } catch (err) {
            toast.error("Error joining campaign");
        } finally {
            setJoiningId(null);
        }
    };

    const copyLink = (url: string, code: string) => {
        navigator.clipboard.writeText(url);
        setCopiedCode(code);
        toast.success("Link copied!");
        setTimeout(() => setCopiedCode(null), 2000);
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <Loader2 className="animate-spin h-8 w-8" />
            </div>
        );
    }

    const totalEarnings = campaigns.reduce((sum, c) => sum + c.my_earnings, 0);
    const totalViews = campaigns.reduce((sum, c) => sum + c.my_views, 0);

    return (
        <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-slate-950 pb-24">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b px-4 py-3">
                <h1 className="font-bold text-xl">Campaigns</h1>
                <p className="text-xs text-muted-foreground">Promote links and earn money</p>
            </header>

            <main className="flex-1 p-4 space-y-6">
                {/* Stats Summary */}
                <div className="grid grid-cols-2 gap-4">
                    <Card>
                        <CardContent className="pt-4">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                                    <DollarSign className="h-5 w-5 text-green-500" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold">${totalEarnings.toFixed(2)}</p>
                                    <p className="text-xs text-muted-foreground">Total Earned</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="pt-4">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                                    <Eye className="h-5 w-5 text-blue-500" />
                                </div>
                                <div>
                                    <p className="text-2xl font-bold">{totalViews}</p>
                                    <p className="text-xs text-muted-foreground">Total Views</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Active Campaigns */}
                <div className="space-y-4">
                    <h2 className="font-semibold text-lg">Available Campaigns</h2>

                    {campaigns.length === 0 ? (
                        <Card>
                            <CardContent className="py-8 text-center text-muted-foreground">
                                <Link2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>No active campaigns right now</p>
                                <p className="text-sm">Check back later!</p>
                            </CardContent>
                        </Card>
                    ) : (
                        campaigns.map(({ campaign, my_link, my_earnings, my_views }) => (
                            <Card key={campaign.id} className="overflow-hidden">
                                <CardHeader className="pb-2">
                                    <div className="flex items-start justify-between">
                                        <CardTitle className="text-lg">{campaign.name}</CardTitle>
                                        <div className="flex items-center gap-1 text-xs bg-emerald-500/10 text-emerald-600 px-2 py-1 rounded-full">
                                            <DollarSign className="h-3 w-3" />
                                            ${campaign.payout_per_view}/view
                                        </div>
                                    </div>
                                    {campaign.description && (
                                        <p className="text-sm text-muted-foreground">{campaign.description}</p>
                                    )}
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {my_link ? (
                                        <>
                                            {/* Already joined - show stats and link */}
                                            <div className="grid grid-cols-2 gap-4 text-sm">
                                                <div className="bg-muted/50 rounded-lg p-3 text-center">
                                                    <p className="text-2xl font-bold">{my_views}</p>
                                                    <p className="text-xs text-muted-foreground">Views</p>
                                                </div>
                                                <div className="bg-muted/50 rounded-lg p-3 text-center">
                                                    <p className="text-2xl font-bold text-green-500">${my_earnings.toFixed(2)}</p>
                                                    <p className="text-xs text-muted-foreground">Earned</p>
                                                </div>
                                            </div>

                                            <div className="space-y-2">
                                                <p className="text-xs font-medium text-muted-foreground">Your Referral Link</p>
                                                <div className="flex gap-2">
                                                    <div className="flex-1 bg-muted rounded-lg px-3 py-2 text-sm font-mono truncate">
                                                        {my_link.full_url}
                                                    </div>
                                                    <Button
                                                        size="icon"
                                                        variant="outline"
                                                        onClick={() => copyLink(my_link.full_url, my_link.short_code)}
                                                    >
                                                        {copiedCode === my_link.short_code ? (
                                                            <Check className="h-4 w-4 text-green-500" />
                                                        ) : (
                                                            <Copy className="h-4 w-4" />
                                                        )}
                                                    </Button>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <Sparkles className="h-3 w-3" />
                                                <span>+{campaign.points_per_view} XP per view</span>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            {/* Not joined yet */}
                                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                                <div className="flex items-center gap-1">
                                                    <DollarSign className="h-4 w-4" />
                                                    ${campaign.payout_per_view} per view
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <Sparkles className="h-4 w-4" />
                                                    +{campaign.points_per_view} XP per view
                                                </div>
                                            </div>

                                            <Button
                                                className="w-full"
                                                onClick={() => handleJoin(campaign.id)}
                                                disabled={joiningId === campaign.id}
                                            >
                                                {joiningId === campaign.id ? (
                                                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                                ) : (
                                                    <Link2 className="h-4 w-4 mr-2" />
                                                )}
                                                Get My Link
                                            </Button>
                                        </>
                                    )}
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            </main>

            {/* Bottom Nav */}
            <nav className="fixed bottom-0 left-0 right-0 bg-background border-t flex justify-around py-3 pb-safe z-20">
                <Link href="/dashboard" className="flex flex-col items-center text-muted-foreground gap-1 hover:text-primary">
                    <Home className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Mission</span>
                </Link>
                <Link href="/campaigns" className="flex flex-col items-center text-primary gap-1">
                    <Link2 className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Campaigns</span>
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
