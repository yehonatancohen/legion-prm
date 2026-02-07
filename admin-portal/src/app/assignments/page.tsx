"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function AssignmentsPage() {
    const [assignments, setAssignments] = useState<any[]>([]);

    const fetchAssignments = () => {
        fetch("http://localhost:8000/api/v1/admin/assignments?status=PENDING", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to fetch");
                return res.json();
            })
            .then((data) => {
                if (Array.isArray(data)) {
                    setAssignments(data);
                } else {
                    console.error("Assignments data is not an array:", data);
                    setAssignments([]);
                }
            })
            .catch(err => {
                console.error(err);
                setAssignments([]);
            });
    };

    useEffect(() => {
        fetchAssignments();
    }, []);

    const handleVerify = async (id: string, status: "VERIFIED" | "REJECTED") => {
        await fetch(`http://localhost:8000/api/v1/admin/assignments/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({ status }),
        });
        fetchAssignments(); // Refresh
    };

    return (
        <div className="flex flex-col gap-4 p-4 md:gap-8 md:p-8">
            <h1 className="text-lg font-semibold md:text-2xl">Pending Reviews</h1>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {assignments.length === 0 && (
                    <div className="col-span-3 text-center text-muted-foreground p-8">No pending assignments.</div>
                )}
                {assignments.map((assignment: any) => (
                    <Card key={assignment.id}>
                        <CardHeader className="flex flex-col gap-1 pb-2">
                            <CardTitle className="text-base">
                                {assignment.campaign.name}
                            </CardTitle>
                            <div className="text-sm text-muted-foreground">
                                Agent: {assignment.agent.name}
                            </div>
                        </CardHeader>
                        <CardContent>
                            {/* Mock Screenshot View */}
                            <div className="aspect-video w-full bg-muted rounded-md mb-4 flex items-center justify-center text-muted-foreground text-xs">
                                {assignment.proof_data ? "Screenshot" : "No Image"}
                            </div>

                            <div className="flex gap-2">
                                <Button
                                    className="flex-1 bg-green-600 hover:bg-green-700"
                                    onClick={() => handleVerify(assignment.id, "VERIFIED")}
                                >
                                    Approve
                                </Button>
                                <Button
                                    variant="destructive"
                                    className="flex-1"
                                    onClick={() => handleVerify(assignment.id, "REJECTED")}
                                >
                                    Reject
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
