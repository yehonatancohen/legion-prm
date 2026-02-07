
"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Clock, Copy, Search, ShieldAlert, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner"; // Assuming sonner is available or will be installed

export default function MonitoringPage() {
    const [agents, setAgents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'WARNING' | 'INACTIVE'>('ALL');

    const fetchAgents = async () => {
        setLoading(true);
        const token = localStorage.getItem("token");
        try {
            const res = await fetch("http://localhost:8000/api/v1/contacts/admin/agents/status", {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) setAgents(await res.json());
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAgents();
    }, []);

    const handleCopyReport = async () => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch("http://localhost:8000/api/v1/contacts/admin/export/text", {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                await navigator.clipboard.writeText(data.report);
                alert("Report copied to clipboard!"); // Fallback if no toast
            }
        } catch (e) {
            alert("Failed to copy report");
        }
    };

    const filteredAgents = agents.filter(agent => {
        if (filter === 'ALL') return true;
        return agent.status === filter;
    });

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ACTIVE': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
            case 'WARNING': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
            case 'INACTIVE': return 'bg-red-500/10 text-red-500 border-red-500/20';
            default: return 'bg-muted text-muted-foreground';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'ACTIVE': return <CheckCircle2 size={16} />;
            case 'WARNING': return <AlertCircle size={16} />;
            case 'INACTIVE': return <XCircle size={16} />;
            default: return <Clock size={16} />;
        }
    };

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Agent Monitoring</h1>
                    <p className="text-muted-foreground">Real-time status tracking and inactivity alerts</p>
                </div>
                <Button onClick={handleCopyReport} variant="outline" className="gap-2">
                    <Copy size={16} />
                    Copy Status Report
                </Button>
            </div>

            {/* Metrics cards */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card className="bg-emerald-50 border-emerald-100 dark:bg-emerald-950/20 dark:border-emerald-900">
                    <CardContent className="p-6">
                        <div className="text-sm font-medium text-emerald-600 dark:text-emerald-400">Active Today</div>
                        <div className="text-2xl font-bold mt-2">
                            {agents.filter(a => a.today_total > 0).length}
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-yellow-50 border-yellow-100 dark:bg-yellow-950/20 dark:border-yellow-900">
                    <CardContent className="p-6">
                        <div className="text-sm font-medium text-yellow-600 dark:text-yellow-400">Warnings</div>
                        <div className="text-2xl font-bold mt-2">
                            {agents.filter(a => a.status === 'WARNING').length}
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-red-50 border-red-100 dark:bg-red-950/20 dark:border-red-900">
                    <CardContent className="p-6">
                        <div className="text-sm font-medium text-red-600 dark:text-red-400">Inactive</div>
                        <div className="text-2xl font-bold mt-2">
                            {agents.filter(a => a.status === 'INACTIVE').length}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-6">
                        <div className="text-sm font-medium text-muted-foreground">Total Contacts (Today)</div>
                        <div className="text-2xl font-bold mt-2">
                            {agents.reduce((sum, a) => sum + a.today_total, 0).toLocaleString()}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters */}
            <div className="flex gap-2 pb-2">
                {(['ALL', 'ACTIVE', 'WARNING', 'INACTIVE'] as const).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors border
                            ${filter === f
                                ? 'bg-primary text-primary-foreground border-primary'
                                : 'bg-background hover:bg-muted text-muted-foreground'
                            }`}
                    >
                        {f.charAt(0) + f.slice(1).toLowerCase()}
                        <span className="ml-2 text-xs opacity-60">
                            {f === 'ALL' ? agents.length : agents.filter(a => a.status === f).length}
                        </span>
                    </button>
                ))}
            </div>

            {/* Agents Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredAgents.map((agent) => (
                    <Card key={agent.id} className="overflow-hidden">
                        <div className="p-5">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="font-bold text-lg">{agent.name}</h3>
                                    <p className="text-sm text-muted-foreground font-mono">{agent.phone}</p>
                                </div>
                                <div className={`px-2 py-1 rounded-full text-xs font-bold border flex items-center gap-1 ${getStatusColor(agent.status)}`}>
                                    {getStatusIcon(agent.status)}
                                    {agent.status}
                                </div>
                            </div>

                            <div className="space-y-3">
                                <div className="space-y-1">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Today's Progress</span>
                                        <span className="font-medium">{agent.today_total} / 50</span>
                                    </div>
                                    <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary transition-all"
                                            style={{ width: `${Math.min(100, (agent.today_total / 50) * 100)}%` }}
                                        />
                                    </div>
                                    <div className="flex justify-between text-xs text-muted-foreground pt-1">
                                        <span>Morning: {agent.today_morning}</span>
                                        <span>Evening: {agent.today_evening}</span>
                                    </div>
                                </div>

                                <div className="pt-3 border-t grid grid-cols-2 gap-2 text-xs">
                                    <div>
                                        <span className="text-muted-foreground block">Total Added</span>
                                        <span className="font-mono font-medium">{agent.total_added.toLocaleString()}</span>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-muted-foreground block">Last Active</span>
                                        <span className={agent.inactive_days > 0 ? "text-destructive font-bold" : ""}>
                                            {agent.inactive_days === 0 ? 'Today' : `${agent.inactive_days}d ago`}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {agent.inactive_days > 1 && (
                            <div className="bg-destructive/10 p-2 text-center text-xs text-destructive font-medium flex items-center justify-center gap-2">
                                <ShieldAlert size={12} />
                                Needs Manager Attention
                            </div>
                        )}
                    </Card>
                ))}
            </div>

            {filteredAgents.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                    <p>No agents found matching this filter.</p>
                </div>
            )}
        </div>
    );
}
