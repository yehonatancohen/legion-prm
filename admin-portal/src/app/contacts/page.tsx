"use client";

import { useEffect, useState } from "react";
import { Upload, FileSpreadsheet, Layers, RefreshCw, UserPlus, UserCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface Agent {
    id: string;
    name: string;
    phone: string;
}

export default function ContactsPage() {
    const [stats, setStats] = useState<any>(null);
    const [uploading, setUploading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [batches, setBatches] = useState<any[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [assigningBatchId, setAssigningBatchId] = useState<string | null>(null);
    const [selectedAgent, setSelectedAgent] = useState<string>("");

    // Form states
    const [prefix, setPrefix] = useState("LEG");
    const [batchSize, setBatchSize] = useState("1500");

    const fetchStats = async () => {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/api/v1/contacts/admin/contacts/pool/stats", {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) setStats(await res.json());
    };

    const fetchBatches = async () => {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/api/v1/contacts/admin/vcf/batches", {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data)) setBatches(data);
        }
    };

    const fetchAgents = async () => {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/api/v1/contacts/admin/agents/status", {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data)) setAgents(data);
        }
    };

    useEffect(() => {
        fetchStats();
        fetchBatches();
        fetchAgents();
    }, []);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;
        setUploading(true);

        const formData = new FormData();
        formData.append("file", e.target.files[0]);

        const token = localStorage.getItem("token");
        try {
            const res = await fetch("http://localhost:8000/api/v1/contacts/admin/contacts/upload", {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
                body: formData
            });
            if (res.ok) {
                const data = await res.json();
                toast.success(`Uploaded! ${data.new_contacts} new contacts added.`);
                fetchStats();
            } else {
                toast.error("Upload failed");
            }
        } catch (err) {
            console.error(err);
            toast.error("Upload error");
        } finally {
            setUploading(false);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        const token = localStorage.getItem("token");
        try {
            const res = await fetch("http://localhost:8000/api/v1/contacts/admin/vcf/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    prefix,
                    contacts_per_batch: parseInt(batchSize),
                    contacts_per_serial: 25,
                    max_batches: 1
                })
            });
            if (res.ok) {
                toast.success("Batch generated!");
                fetchBatches();
                fetchStats();
            } else {
                toast.error("Generation failed");
            }
        } finally {
            setGenerating(false);
        }
    };

    const handleAssign = async (batchId: string) => {
        if (!selectedAgent) {
            toast.error("Please select an agent");
            return;
        }

        const token = localStorage.getItem("token");
        try {
            const res = await fetch(`http://localhost:8000/api/v1/contacts/admin/vcf/batches/${batchId}/assign`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ agent_id: selectedAgent })
            });
            if (res.ok) {
                toast.success("Batch assigned!");
                setAssigningBatchId(null);
                setSelectedAgent("");
                fetchBatches();
            } else {
                toast.error("Assignment failed");
            }
        } catch (err) {
            toast.error("Assignment error");
        }
    };

    return (
        <div className="flex flex-col gap-6">
            <h1 className="text-2xl font-bold tracking-tight">Contact Management</h1>

            {/* Top Stats Row */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Total Contacts</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_contacts?.toLocaleString() || 0}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Unassigned Pool</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.unassigned?.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground">{stats?.assignment_rate || 0}% assigned</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Active Batches</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{batches.filter(b => b.status !== 'COMPLETED').length}</div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">

                {/* Upload Section */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Upload className="w-5 h-5 text-primary" />
                            Upload Contacts
                        </CardTitle>
                        <CardDescription>
                            Import Excel files (.xlsx) with phone numbers.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-center w-full border-2 border-dashed rounded-lg p-6 hover:bg-muted/50 transition-colors cursor-pointer relative bg-muted/20">
                            <input
                                type="file"
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                accept=".xlsx, .xls"
                                onChange={handleUpload}
                                disabled={uploading}
                            />
                            <div className="text-center space-y-2">
                                <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                                    <FileSpreadsheet />
                                </div>
                                <div className="font-medium">
                                    {uploading ? "Uploading..." : "Click to select Excel file"}
                                </div>
                                <p className="text-xs text-muted-foreground">Supported format: .xlsx</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Generate Section */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Layers className="w-5 h-5 text-primary" />
                            Generate VCF Batch
                        </CardTitle>
                        <CardDescription>
                            Create a new batch of contacts for an agent.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Serial Prefix</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    value={prefix}
                                    onChange={(e) => setPrefix(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Batch Size</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    type="number"
                                    value={batchSize}
                                    onChange={(e) => setBatchSize(e.target.value)}
                                />
                            </div>
                        </div>
                        <Button className="w-full" onClick={handleGenerate} disabled={generating || stats?.unassigned === 0}>
                            {generating ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <UserPlus className="mr-2 h-4 w-4" />}
                            Generate Next Batch
                        </Button>
                        {stats?.unassigned === 0 && (
                            <p className="text-xs text-center text-destructive">No unassigned contacts available.</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Batches List */}
            <Card>
                <CardHeader>
                    <CardTitle>Recent Batches</CardTitle>
                    <CardDescription>Click "Assign" to assign a batch to an agent</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-muted/50 text-muted-foreground font-medium border-b">
                                <tr>
                                    <th className="px-4 py-3">Batch ID</th>
                                    <th className="px-4 py-3">Prefix</th>
                                    <th className="px-4 py-3">Size</th>
                                    <th className="px-4 py-3">Status</th>
                                    <th className="px-4 py-3">Assigned To</th>
                                    <th className="px-4 py-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {batches.map((batch) => (
                                    <tr key={batch.id} className="hover:bg-muted/10">
                                        <td className="px-4 py-3 font-mono text-xs">{batch.id.substring(0, 8)}...</td>
                                        <td className="px-4 py-3">{batch.prefix}</td>
                                        <td className="px-4 py-3">{batch.contact_count}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded text-xs font-medium 
                                                ${batch.status === 'PENDING' ? 'bg-yellow-500/10 text-yellow-500' : ''}
                                                ${batch.status === 'ASSIGNED' ? 'bg-blue-500/10 text-blue-500' : ''}
                                                ${batch.status === 'IN_PROGRESS' ? 'bg-indigo-500/10 text-indigo-500' : ''}
                                                ${batch.status === 'COMPLETED' ? 'bg-green-500/10 text-green-500' : ''}
                                            `}>
                                                {batch.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">{batch.agent_name || '-'}</td>
                                        <td className="px-4 py-3">
                                            {batch.status === 'PENDING' && (
                                                <>
                                                    {assigningBatchId === batch.id ? (
                                                        <div className="flex gap-2 items-center">
                                                            <select
                                                                className="h-8 rounded border border-input bg-background px-2 text-xs"
                                                                value={selectedAgent}
                                                                onChange={(e) => setSelectedAgent(e.target.value)}
                                                            >
                                                                <option value="">Select agent...</option>
                                                                {agents.map(agent => (
                                                                    <option key={agent.id} value={agent.id}>{agent.name}</option>
                                                                ))}
                                                            </select>
                                                            <Button size="sm" onClick={() => handleAssign(batch.id)}>
                                                                <UserCheck className="h-3 w-3" />
                                                            </Button>
                                                            <Button size="sm" variant="ghost" onClick={() => setAssigningBatchId(null)}>
                                                                ✕
                                                            </Button>
                                                        </div>
                                                    ) : (
                                                        <Button size="sm" variant="outline" onClick={() => setAssigningBatchId(batch.id)}>
                                                            Assign
                                                        </Button>
                                                    )}
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                                {batches.length === 0 && (
                                    <tr>
                                        <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                                            No batches generated yet. Use the tool above.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
