"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AgentsPage() {
    const [agents, setAgents] = useState<any[]>([]);

    useEffect(() => {
        fetch("http://localhost:8000/api/v1/admin/agents", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to fetch");
                return res.json();
            })
            .then((data) => {
                if (Array.isArray(data)) {
                    setAgents(data);
                } else {
                    console.error("Agents data is not an array:", data);
                    setAgents([]);
                }
            })
            .catch(err => {
                console.error(err);
                setAgents([]);
            });
    }, []);

    return (
        <div className="flex flex-col gap-4 p-4 md:gap-8 md:p-8">
            <h1 className="text-lg font-semibold md:text-2xl">Agents</h1>
            <Card>
                <CardHeader>
                    <CardTitle>Field Team</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="relative w-full overflow-auto">
                        <table className="w-full caption-bottom text-sm text-left">
                            <thead className="[&_tr]:border-b">
                                <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Name</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Phone</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Score</th>
                                    <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Wallet</th>
                                </tr>
                            </thead>
                            <tbody className="[&_tr:last-child]:border-0">
                                {agents.map((agent) => (
                                    <tr key={agent.id} className="border-b transition-colors hover:bg-muted/50">
                                        <td className="p-4 align-middle font-medium">{agent.name}</td>
                                        <td className="p-4 align-middle">{agent.phone}</td>
                                        <td className="p-4 align-middle">{agent.current_score} pts</td>
                                        <td className="p-4 align-middle">${agent.wallet_balance}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
