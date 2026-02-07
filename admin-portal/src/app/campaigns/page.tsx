"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Plus, Link2, Copy, Eye, DollarSign, Users, Pause, Play, RefreshCw } from "lucide-react";

interface Campaign {
    id: string;
    name: string;
    description: string | null;
    target_url: string;
    status: string;
    payout_per_view: number;
    points_per_view: number;
    budget_cap: number;
    spent: number;
    total_views: number;
    total_unique_views: number;
    created_at: string;
}

export default function CampaignsPage() {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [creating, setCreating] = useState(false);

    // Form state
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [targetUrl, setTargetUrl] = useState("");
    const [payoutPerView, setPayoutPerView] = useState("0.01");
    const [pointsPerView, setPointsPerView] = useState("1");
    const [budgetCap, setBudgetCap] = useState("100");

    const fetchCampaigns = async () => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch("http://localhost:8000/api/v1/campaigns/admin/campaigns", {
                headers: { Authorization: `Bearer ${token}` }
            });
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

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name || !targetUrl) {
            toast.error("Name and URL are required");
            return;
        }

        setCreating(true);
        const token = localStorage.getItem("token");

        try {
            const res = await fetch("http://localhost:8000/api/v1/campaigns/admin/campaigns", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    name,
                    description: description || null,
                    target_url: targetUrl,
                    payout_per_view: parseFloat(payoutPerView),
                    points_per_view: parseInt(pointsPerView),
                    budget_cap: parseFloat(budgetCap)
                })
            });

            if (res.ok) {
                toast.success("Campaign created!");
                setShowCreate(false);
                setName("");
                setDescription("");
                setTargetUrl("");
                fetchCampaigns();
            } else {
                const err = await res.json();
                toast.error(err.detail || "Failed to create campaign");
            }
        } catch (err) {
            toast.error("Error creating campaign");
        } finally {
            setCreating(false);
        }
    };

    const handleStatusChange = async (campaignId: string, newStatus: string) => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch(
                `http://localhost:8000/api/v1/campaigns/admin/campaigns/${campaignId}/status?status=${newStatus}`,
                {
                    method: "PATCH",
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            if (res.ok) {
                toast.success(`Campaign ${newStatus.toLowerCase()}`);
                fetchCampaigns();
            }
        } catch (err) {
            toast.error("Failed to update status");
        }
    };

    const copyShortUrl = (campaignId: string) => {
        // This would need the short code - for now just show a message
        toast.info("Agents will get unique links when they join");
    };

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Campaigns</h1>
                    <p className="text-muted-foreground">Create and manage promotional campaigns</p>
                </div>
                <Button onClick={() => setShowCreate(!showCreate)}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Campaign
                </Button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <Card>
                    <CardHeader>
                        <CardTitle>Create Campaign</CardTitle>
                        <CardDescription>
                            Set up a link promotion campaign. Agents will get unique referral links.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div className="grid gap-4 md:grid-cols-2">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Campaign Name *</label>
                                    <input
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        placeholder="Summer Sale Promo"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Target URL *</label>
                                    <input
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        placeholder="https://example.com/landing-page"
                                        value={targetUrl}
                                        onChange={(e) => setTargetUrl(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Description</label>
                                <textarea
                                    className="flex min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    placeholder="Brief description for agents..."
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                />
                            </div>

                            <div className="grid gap-4 md:grid-cols-3">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Payout per View ($)</label>
                                    <input
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        type="number"
                                        step="0.001"
                                        min="0"
                                        value={payoutPerView}
                                        onChange={(e) => setPayoutPerView(e.target.value)}
                                    />
                                    <p className="text-xs text-muted-foreground">Money earned per unique view</p>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Points per View</label>
                                    <input
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        type="number"
                                        min="0"
                                        value={pointsPerView}
                                        onChange={(e) => setPointsPerView(e.target.value)}
                                    />
                                    <p className="text-xs text-muted-foreground">XP earned per unique view</p>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Budget Cap ($)</label>
                                    <input
                                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                        type="number"
                                        step="1"
                                        min="1"
                                        value={budgetCap}
                                        onChange={(e) => setBudgetCap(e.target.value)}
                                    />
                                    <p className="text-xs text-muted-foreground">Max total payout</p>
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <Button type="button" variant="ghost" onClick={() => setShowCreate(false)}>
                                    Cancel
                                </Button>
                                <Button type="submit" disabled={creating}>
                                    {creating ? "Creating..." : "Create Campaign"}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* Campaigns Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {campaigns.map((campaign) => (
                    <Card key={campaign.id} className={campaign.status !== "ACTIVE" ? "opacity-60" : ""}>
                        <CardHeader className="pb-2">
                            <div className="flex items-start justify-between">
                                <div>
                                    <CardTitle className="text-lg">{campaign.name}</CardTitle>
                                    <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                                        {campaign.target_url}
                                    </p>
                                </div>
                                <span className={`text-xs px-2 py-1 rounded-full font-medium ${campaign.status === "ACTIVE" ? "bg-green-500/10 text-green-500" :
                                        campaign.status === "PAUSED" ? "bg-yellow-500/10 text-yellow-500" :
                                            "bg-gray-500/10 text-gray-500"
                                    }`}>
                                    {campaign.status}
                                </span>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {campaign.description && (
                                <p className="text-sm text-muted-foreground">{campaign.description}</p>
                            )}

                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="flex items-center gap-2">
                                    <Eye className="h-4 w-4 text-muted-foreground" />
                                    <span>{campaign.total_unique_views} views</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                                    <span>${campaign.spent.toFixed(2)} / ${campaign.budget_cap}</span>
                                </div>
                                <div className="flex items-center gap-2 text-muted-foreground">
                                    <Users className="h-4 w-4" />
                                    <span>${campaign.payout_per_view}/view</span>
                                </div>
                                <div className="flex items-center gap-2 text-muted-foreground">
                                    <span className="text-xs">+{campaign.points_per_view} pts/view</span>
                                </div>
                            </div>

                            {/* Budget progress */}
                            <div className="space-y-1">
                                <div className="flex justify-between text-xs text-muted-foreground">
                                    <span>Budget Used</span>
                                    <span>{Math.round((campaign.spent / campaign.budget_cap) * 100)}%</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-primary transition-all"
                                        style={{ width: `${Math.min(100, (campaign.spent / campaign.budget_cap) * 100)}%` }}
                                    />
                                </div>
                            </div>

                            <div className="flex gap-2">
                                {campaign.status === "ACTIVE" ? (
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleStatusChange(campaign.id, "PAUSED")}
                                    >
                                        <Pause className="h-3 w-3 mr-1" />
                                        Pause
                                    </Button>
                                ) : campaign.status === "PAUSED" ? (
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleStatusChange(campaign.id, "ACTIVE")}
                                    >
                                        <Play className="h-3 w-3 mr-1" />
                                        Resume
                                    </Button>
                                ) : null}
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {campaigns.length === 0 && (
                    <Card className="col-span-full">
                        <CardContent className="py-12 text-center text-muted-foreground">
                            <Link2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <p>No campaigns yet. Create one to get started!</p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
