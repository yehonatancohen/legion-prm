"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

const data = [
    { name: "Mon", clicks: 400 },
    { name: "Tue", clicks: 300 },
    { name: "Wed", clicks: 200 },
    { name: "Thu", clicks: 278 },
    { name: "Fri", clicks: 189 },
    { name: "Sat", clicks: 239 },
    { name: "Sun", clicks: 349 },
];

export default function AnalyticsPage() {
    return (
        <div className="flex flex-col gap-4 p-4 md:gap-8 md:p-8">
            <h1 className="text-lg font-semibold md:text-2xl">Analytics</h1>

            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Clicks Over Time</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data}>
                                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                                <Tooltip />
                                <Line type="monotone" dataKey="clicks" stroke="#8884d8" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Top Traffic Sources</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-medium leading-none">WhatsApp</p>
                                    <p className="text-sm text-muted-foreground">Groups & Direct</p>
                                </div>
                                <div className="ml-auto font-medium">78%</div>
                            </div>
                            <div className="flex items-center">
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-medium leading-none">Instagram</p>
                                    <p className="text-sm text-muted-foreground">Stories</p>
                                </div>
                                <div className="ml-auto font-medium">12%</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
