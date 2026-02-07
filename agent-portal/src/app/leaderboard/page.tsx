"use client";

import Link from "next/link";
import { Trophy, Home, User } from "lucide-react";
import { useEffect, useState } from "react";

export default function LeaderboardPage() {
    const [leaders, setLeaders] = useState<any[]>([]);

    useEffect(() => {
        // Fetch Real Leaderboard
        fetch("http://localhost:8000/api/v1/agent/leaderboard", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        })
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) setLeaders(data);
                else setLeaders([
                    { name: "Bob Agent", current_score: 3500 },
                    { name: "Charlie", current_score: 2800 },
                    { name: "You", current_score: 1250 },
                ]); // Fallback
            })
            .catch(() => setLeaders([
                { name: "Bob Agent", current_score: 3500 },
                { name: "Charlie", current_score: 2800 },
                { name: "You", current_score: 1250 },
            ]));
    }, []);

    return (
        <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-slate-950 pb-20">
            <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b px-4 py-3 text-center">
                <h1 className="font-bold text-xl">Leaderboard</h1>
            </header>

            <main className="flex-1 p-4 space-y-2">
                {leaders.map((agent, i) => (
                    <div key={i} className={`flex items-center gap-4 p-4 rounded-xl border ${i === 0 ? 'bg-yellow-500/10 border-yellow-500/50' : 'bg-card'}`}>
                        <div className={`flex h-8 w-8 items-center justify-center rounded-full font-bold ${i === 0 ? 'text-yellow-600' : 'text-muted-foreground'}`}>
                            #{i + 1}
                        </div>
                        <div className="flex-1 font-medium">
                            {agent.name}
                        </div>
                        <div className="font-bold text-muted-foreground">
                            {agent.current_score} XP
                        </div>
                    </div>
                ))}
            </main>

            <nav className="fixed bottom-0 left-0 right-0 bg-background border-t flex justify-around py-3 pb-safe z-20">
                <Link href="/dashboard" className="flex flex-col items-center text-muted-foreground gap-1 hover:text-primary">
                    <Home className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Tasks</span>
                </Link>
                <Link href="/leaderboard" className="flex flex-col items-center text-primary gap-1">
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
