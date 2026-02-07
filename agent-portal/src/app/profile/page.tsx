"use client";

import Link from "next/link";
import { Trophy, Home, User, LogOut } from "lucide-react";

export default function ProfilePage() {
    return (
        <div className="flex min-h-screen flex-col bg-slate-50 dark:bg-slate-950 pb-20">
            <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b px-4 py-3 text-center">
                <h1 className="font-bold text-xl">Profile</h1>
            </header>

            <main className="flex-1 p-4 space-y-6">
                <div className="flex flex-col items-center text-center space-y-2 mt-8">
                    <div className="h-20 w-20 bg-primary/20 rounded-full flex items-center justify-center text-3xl">
                        😎
                    </div>
                    <div>
                        <h2 className="text-xl font-bold">Agent Demo</h2>
                        <p className="text-muted-foreground">+1 (555) 123-4567</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-card p-4 rounded-xl border text-center">
                        <div className="text-2xl font-bold">1,250</div>
                        <div className="text-xs text-muted-foreground uppercase tracking-widest">Total XP</div>
                    </div>
                    <div className="bg-card p-4 rounded-xl border text-center">
                        <div className="text-2xl font-bold">$450</div>
                        <div className="text-xs text-muted-foreground uppercase tracking-widest">Balance</div>
                    </div>
                </div>

                <button className="w-full flex items-center justify-center gap-2 p-4 text-red-500 bg-red-500/10 rounded-xl font-bold mt-auto">
                    <LogOut className="h-5 w-5" />
                    Sign Out
                </button>
            </main>

            <nav className="fixed bottom-0 left-0 right-0 bg-background border-t flex justify-around py-3 pb-safe z-20">
                <Link href="/dashboard" className="flex flex-col items-center text-muted-foreground gap-1 hover:text-primary">
                    <Home className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Tasks</span>
                </Link>
                <Link href="/leaderboard" className="flex flex-col items-center text-muted-foreground gap-1 hover:text-primary">
                    <Trophy className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Leaderboard</span>
                </Link>
                <Link href="/profile" className="flex flex-col items-center text-primary gap-1">
                    <User className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Profile</span>
                </Link>
            </nav>
        </div>
    );
}
