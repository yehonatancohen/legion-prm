"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Users, MousePointerClick, Megaphone, Trophy, Layers, Activity, ArrowRight, LogOut, RefreshCw } from "lucide-react";

interface DashboardStats {
  total_agents: number;
  total_campaigns: number;
  total_clicks: number;
  top_agents: any[];
}

interface ContactStats {
  total_contacts: number;
  assigned: number;
  unassigned: number;
  assignment_rate: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [contactStats, setContactStats] = useState<ContactStats | null>(null);
  const [agentStatuses, setAgentStatuses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchData = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      // Fetch main dashboard stats
      const statsRes = await fetch("http://localhost:8000/api/v1/admin/dashboard/stats", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      } else if (statsRes.status === 401 || statsRes.status === 403) {
        localStorage.removeItem("token");
        router.push("/login");
        return;
      }

      // Fetch contact pool stats
      const contactRes = await fetch("http://localhost:8000/api/v1/contacts/admin/contacts/pool/stats", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (contactRes.ok) {
        setContactStats(await contactRes.json());
      }

      // Fetch agent statuses
      const agentRes = await fetch("http://localhost:8000/api/v1/contacts/admin/agents/status", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (agentRes.ok) {
        const data = await agentRes.json();
        if (Array.isArray(data)) setAgentStatuses(data);
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const activeToday = agentStatuses.filter(a => a.today_total > 0).length;
  const inactiveAgents = agentStatuses.filter(a => a.status === 'INACTIVE').length;
  const todayContacts = agentStatuses.reduce((sum, a) => sum + a.today_total, 0);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Legion Command Center</h1>
          <p className="text-muted-foreground">Real-time overview of your operation</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_agents || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-emerald-500 font-medium">{activeToday}</span> active today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Contact Pool</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{contactStats?.total_contacts?.toLocaleString() || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-blue-500 font-medium">{contactStats?.unassigned?.toLocaleString() || 0}</span> available
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Contacts</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayContacts}</div>
            <p className="text-xs text-muted-foreground">
              Added by agents today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Campaigns</CardTitle>
            <Megaphone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_campaigns || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active operations
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common management tasks</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2">
            <Link href="/contacts">
              <Button variant="outline" className="w-full justify-between">
                Upload Contacts
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/contacts">
              <Button variant="outline" className="w-full justify-between">
                Generate VCF Batch
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/monitoring">
              <Button variant="outline" className="w-full justify-between">
                View Agent Status
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Top Agents */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-amber-500" />
              Top Performers
            </CardTitle>
            <CardDescription>Highest XP this week</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {(stats?.top_agents || []).slice(0, 5).map((agent, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold
                  ${i === 0 ? 'bg-amber-500/20 text-amber-600' : ''}
                  ${i === 1 ? 'bg-slate-400/20 text-slate-500' : ''}
                  ${i === 2 ? 'bg-orange-400/20 text-orange-500' : ''}
                  ${i > 2 ? 'bg-muted text-muted-foreground' : ''}
                `}>
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{agent.name}</p>
                  <p className="text-xs text-muted-foreground">{agent.score || 0} XP</p>
                </div>
              </div>
            ))}
            {(!stats?.top_agents || stats.top_agents.length === 0) && (
              <p className="text-sm text-muted-foreground text-center py-4">No agents yet</p>
            )}
          </CardContent>
        </Card>

        {/* Attention Required */}
        <Card className={inactiveAgents > 0 ? "border-destructive/50" : ""}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {inactiveAgents > 0 && <span className="h-2 w-2 rounded-full bg-destructive animate-pulse" />}
              Needs Attention
            </CardTitle>
            <CardDescription>Agents requiring follow-up</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {agentStatuses
              .filter(a => a.status === 'INACTIVE' || a.status === 'WARNING')
              .slice(0, 5)
              .map((agent, i) => (
                <div key={i} className="flex items-center justify-between gap-2 text-sm">
                  <span className="truncate font-medium">{agent.name}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${agent.status === 'INACTIVE' ? 'bg-destructive/10 text-destructive' : 'bg-yellow-500/10 text-yellow-600'
                    }`}>
                    {agent.inactive_days}d inactive
                  </span>
                </div>
              ))}
            {agentStatuses.filter(a => a.status === 'INACTIVE' || a.status === 'WARNING').length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                ✓ All agents are active
              </p>
            )}
            {inactiveAgents > 0 && (
              <Link href="/monitoring">
                <Button variant="outline" size="sm" className="w-full mt-2">
                  View All
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
