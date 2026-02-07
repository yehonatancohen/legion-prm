"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Home, Users, Megaphone, CheckSquare, Layers, Activity } from "lucide-react";

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="hidden border-r bg-muted/40 md:block w-64 h-full fixed top-0 left-0 bottom-0 z-30">
            <div className="flex h-full max-h-screen flex-col gap-2">
                <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
                    <Link href="/" className="flex items-center gap-2 font-bold text-lg text-primary">
                        <span>Legion Command</span>
                    </Link>
                </div>
                <div className="flex-1 overflow-auto py-2">
                    <nav className="grid items-start px-2 text-sm font-medium lg:px-4 space-y-1">

                        <div className="text-xs font-bold text-muted-foreground mt-4 mb-2 px-3">OVERVIEW</div>

                        <NavItem href="/" icon={Home} label="Dashboard" active={pathname === "/"} />
                        <NavItem href="/analytics" icon={BarChart3} label="Analytics" active={pathname === "/analytics"} />

                        <div className="text-xs font-bold text-muted-foreground mt-4 mb-2 px-3">OPERATIONS</div>

                        <NavItem href="/monitoring" icon={Activity} label="Live Monitoring" active={pathname === "/monitoring"} />
                        <NavItem href="/contacts" icon={Layers} label="Contact Pool" active={pathname === "/contacts"} />
                        <NavItem href="/assignments" icon={CheckSquare} label="Assignments" active={pathname === "/assignments"} />

                        <div className="text-xs font-bold text-muted-foreground mt-4 mb-2 px-3">MANAGEMENT</div>

                        <NavItem href="/campaigns" icon={Megaphone} label="Campaigns" active={pathname === "/campaigns"} />
                        <NavItem href="/agents" icon={Users} label="Agents" active={pathname === "/agents"} />

                    </nav>
                </div>
            </div>
        </div>
    )
}

function NavItem({ href, icon: Icon, label, active }: { href: string; icon: any; label: string; active: boolean }) {
    return (
        <Link
            href={href}
            className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary hover:bg-muted ${active ? "bg-muted text-primary font-medium" : "text-muted-foreground"
                }`}
        >
            <Icon className="h-4 w-4" />
            {label}
        </Link>
    );
}

