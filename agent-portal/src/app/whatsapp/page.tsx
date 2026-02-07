"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Copy, Download, CheckCircle, Info, Send, Trophy, Home, User } from "lucide-react";

export default function WhatsappPage() {
    const [activeTab, setActiveTab] = useState("task");
    const [batches, setBatches] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [reportCount, setReportCount] = useState(25);
    const [reportNotes, setReportNotes] = useState("");

    // Fetch batches
    useEffect(() => {
        const token = localStorage.getItem("token");
        fetch("http://localhost:8000/api/v1/whatsapp/my-batches", {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(res => res.ok ? res.json() : []) // Mock handled via backend if empty
            .then(data => {
                // Mock data if empty for visualization
                if (data.length === 0) {
                    setBatches([{
                        id: "demo-batch",
                        contact_count: 1000,
                        target_group_name: "Mega Party Group 1",
                        status: "ASSIGNED",
                        vcf_file_path: "/mock.vcf"
                    }]);
                } else {
                    setBatches(data);
                }
                setLoading(false);
            });
    }, []);

    const submitReport = async () => {
        const token = localStorage.getItem("token");
        const batchId = batches[0]?.id; // detailed logic later
        if (!batchId) return;

        await fetch(`http://localhost:8000/api/v1/whatsapp/batches/${batchId}/report`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ added_count: reportCount, notes: reportNotes })
        });
        alert("Report Submitted! Great work.");
    };

    return (
        <div className="flex min-h-screen flex-col bg-slate-900 text-slate-100 pb-24 font-sans">
            {/* Header */}
            <header className="sticky top-0 z-30 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 px-4 py-4 flex items-center justify-between shadow-lg">
                <h1 className="font-extrabold text-xl bg-gradient-to-r from-green-400 to-emerald-600 bg-clip-text text-transparent">WhatsApp Ops</h1>
                <div className="bg-slate-800 px-3 py-1 rounded-full text-xs font-bold border border-slate-700 text-green-400">
                    Online
                </div>
            </header>

            <main className="flex-1 p-4 space-y-6">

                {/* Tabs */}
                <div className="flex p-1 bg-slate-800/50 rounded-xl">
                    {["task", "report", "guide"].map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === tab ? "bg-emerald-600 text-white shadow-lg" : "text-slate-400 hover:text-slate-200"}`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>

                {activeTab === "task" && (
                    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {batches.map(batch => (
                            <div key={batch.id} className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl relative overflow-hidden group">
                                <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
                                <h2 className="text-xl font-bold mb-2 text-white">Your Mission</h2>
                                <p className="text-slate-400 text-sm mb-4">Target Group: <span className="text-emerald-400 font-mono font-bold">{batch.target_group_name || "Unassigned"}</span></p>

                                <div className="bg-slate-900/50 rounded-xl p-4 mb-4 border border-slate-700/50">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-xs uppercase tracking-wider text-slate-500">Database Size</span>
                                        <span className="font-bold text-emerald-400">{batch.contact_count} Contacts</span>
                                    </div>
                                    <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                                        <div className="bg-emerald-500 h-full w-[10%]"></div>
                                    </div>
                                    <p className="text-xs text-right mt-1 text-slate-500">10% Complete</p>
                                </div>

                                <button className="w-full py-4 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500 text-white rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/20 transition-all transform hover:scale-[1.02]">
                                    <Download className="w-5 h-5" /> Download VCF Batch
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === "report" && (
                    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl">
                            <h3 className="font-bold text-lg mb-4">Daily Report</h3>

                            <label className="block text-sm text-slate-400 mb-2">People Added Today</label>
                            <div className="flex items-center gap-4 mb-6">
                                <button onClick={() => setReportCount(Math.max(0, reportCount - 5))} className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center text-xl font-bold hover:bg-slate-600 transition">-</button>
                                <span className="text-3xl font-bold w-16 text-center">{reportCount}</span>
                                <button onClick={() => setReportCount(reportCount + 5)} className="w-12 h-12 rounded-full bg-emerald-600 flex items-center justify-center text-xl font-bold hover:bg-emerald-500 transition">+</button>
                            </div>

                            <label className="block text-sm text-slate-400 mb-2">Notes / Issues</label>
                            <textarea
                                value={reportNotes}
                                onChange={(e) => setReportNotes(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 mb-6 focus:ring-2 focus:ring-emerald-500 outline-none transition"
                                rows={3}
                                placeholder="Any problems with the group?"
                            />

                            <button onClick={submitReport} className="w-full py-4 bg-white text-slate-900 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-slate-200 transition">
                                <Send className="w-5 h-5" /> Submit Report
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === "guide" && (
                    <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl animate-in fade-in slide-in-from-bottom-4">
                        <h3 className="font-bold text-lg mb-4 flex items-center gap-2"><Info className="text-blue-400" /> Instructions</h3>
                        <ul className="space-y-4 text-sm text-slate-300">
                            <li className="flex gap-3"><CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" /> Download your designated VCF file.</li>
                            <li className="flex gap-3"><CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" /> Import it to your phone contacts.</li>
                            <li className="flex gap-3"><CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" /> Go to the WhatsApp Group.</li>
                            <li className="flex gap-3"><CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" /> Add 25-50 people from the top of the list.</li>
                        </ul>
                    </div>
                )}
            </main>

            {/* Nav */}
            <nav className="fixed bottom-0 left-0 right-0 bg-slate-900/90 backdrop-blur-xl border-t border-slate-800 flex justify-around py-4 pb-safe z-40">
                <Link href="/dashboard" className="flex flex-col items-center text-slate-500 gap-1 hover:text-white transition">
                    <Home className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Home</span>
                </Link>
                <button className="flex flex-col items-center text-emerald-500 gap-1">
                    <div className="relative">
                        <div className="absolute -inset-1 bg-emerald-500/20 blur-lg rounded-full"></div>
                        <Send className="h-6 w-6 relative z-10" />
                    </div>
                    <span className="text-[10px] font-medium">WhatsApp</span>
                </button>
                <Link href="/leaderboard" className="flex flex-col items-center text-slate-500 gap-1 hover:text-white transition">
                    <Trophy className="h-6 w-6" />
                    <span className="text-[10px] font-medium">Rank</span>
                </Link>
            </nav>
        </div>
    );
}
