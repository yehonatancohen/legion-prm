
"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar, Moon, Sun, Upload, CheckCircle2 } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import { TodayProgress } from "@/types/contacts";

interface ProgressTrackerProps {
    initialProgress: TodayProgress | null;
    onUpdate: () => void;
}

export function ProgressTracker({ initialProgress, onUpdate }: ProgressTrackerProps) {
    const [session, setSession] = useState<'morning' | 'evening' | null>(null);
    const [count, setCount] = useState(25);
    const [notes, setNotes] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    // If no initial progress, use default empty
    const progress = initialProgress || {
        date: new Date().toISOString(),
        morning_count: 0,
        evening_count: 0,
        total: 0,
        goal: 50,
        progress_percent: 0,
    };

    const handleReport = async (sessionType: 'morning' | 'evening') => {
        setSession(sessionType);
        setCount(25); // Default expected count
        setNotes("");
    };

    const submitReport = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!session) return;

        setIsSubmitting(true);
        const token = localStorage.getItem("token");

        try {
            // First, get the active batch ID
            const batchesRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/contacts/agent/vcf/batches`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!batchesRes.ok) {
                toast.error("Failed to fetch batches. Please try again.");
                setIsSubmitting(false);
                return;
            }

            const batches = await batchesRes.json();

            if (!Array.isArray(batches) || batches.length === 0) {
                toast.error("No active batch assigned. Please contact admin.");
                setIsSubmitting(false);
                return;
            }

            const activeBatch = batches[0]; // Active is usually first/latest

            if (!activeBatch || !activeBatch.id) {
                toast.error("Invalid batch data. Please contact admin.");
                setIsSubmitting(false);
                return;
            }

            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/contacts/agent/progress/report`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    batch_id: activeBatch.id,
                    session_type: session,
                    count: count,
                    notes: notes,
                }),
            });

            if (!res.ok) throw new Error("Failed to report progress");

            toast.success(`${session === 'morning' ? 'Morning' : 'Evening'} report submitted!`);
            setSession(null);
            onUpdate();

        } catch (error) {
            console.error(error);
            toast.error("Error submitting report");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-primary" />
                    Today's Mission
                </CardTitle>
                <CardDescription>
                    Target: {progress.goal} contacts ({format(new Date(), "MMMM do, yyyy")})
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">

                {/* Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between text-sm font-medium">
                        <span>Progress</span>
                        <span className={progress.total >= progress.goal ? "text-green-600" : "text-muted-foreground"}>
                            {progress.total} / {progress.goal}
                        </span>
                    </div>
                    <Progress value={progress.progress_percent} className="h-2" />
                </div>

                {/* Action Buttons */}
                {!session ? (
                    <div className="grid grid-cols-2 gap-4">
                        <Button
                            variant={progress.morning_count > 0 ? "secondary" : "default"}
                            className="h-24 flex flex-col gap-2"
                            onClick={() => handleReport('morning')}
                            disabled={progress.morning_count > 0}
                        >
                            <Sun className={`w-8 h-8 ${progress.morning_count > 0 ? 'text-green-600' : 'text-yellow-500'}`} />
                            <div>
                                <span className="font-bold block">Morning</span>
                                <span className="text-xs text-muted-foreground">
                                    {progress.morning_count > 0 ? "Completed ✓" : "+25 Contacts"}
                                </span>
                            </div>
                        </Button>

                        <Button
                            variant={progress.evening_count > 0 ? "secondary" : "default"}
                            className="h-24 flex flex-col gap-2"
                            onClick={() => handleReport('evening')}
                            disabled={progress.evening_count > 0}
                        >
                            <Moon className={`w-8 h-8 ${progress.evening_count > 0 ? 'text-green-600' : 'text-blue-400'}`} />
                            <div>
                                <span className="font-bold block">Evening</span>
                                <span className="text-xs text-muted-foreground">
                                    {progress.evening_count > 0 ? "Completed ✓" : "+25 Contacts"}
                                </span>
                            </div>
                        </Button>
                    </div>
                ) : (
                    <form onSubmit={submitReport} className="space-y-4 border p-4 rounded-lg bg-card/50">
                        <h3 className="font-semibold flex items-center gap-2">
                            Report {session === 'morning' ? 'Morning' : 'Evening'} Session
                        </h3>

                        <div className="space-y-2">
                            <Label htmlFor="count">Contacts Added</Label>
                            <Input
                                id="count"
                                type="number"
                                value={count}
                                onChange={(e) => setCount(Number(e.target.value))}
                                min={0}
                                max={50}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="notes">Notes (Optional)</Label>
                            <Textarea
                                id="notes"
                                placeholder="Any issues? e.g., 'WhatsApp blocked me temporarily'"
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                            />
                        </div>

                        <div className="flex gap-2">
                            <Button type="button" variant="ghost" onClick={() => setSession(null)}>Cancel</Button>
                            <Button type="submit" disabled={isSubmitting}>
                                {isSubmitting ? "Submitting..." : "Confirm Report"}
                            </Button>
                        </div>
                    </form>
                )}

            </CardContent>
        </Card>
    );
}
