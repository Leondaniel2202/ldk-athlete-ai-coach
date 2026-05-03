"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import StatusBadge from "@/components/ui/StatusBadge";
import { useBackendStatus } from "@/hooks/useBackendStatus";

const navigationItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/planner", label: "Planner" },
  { href: "/analyzer", label: "Analyzer" },
  { href: "/coach", label: "Coach" },
];

interface AppShellProps {
  children: ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const backendStatus = useBackendStatus();

  return (
    <div className="min-h-screen bg-stone-50 text-zinc-950">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col lg:flex-row">
        <aside className="border-b border-zinc-200 bg-white px-5 py-4 lg:w-64 lg:border-r lg:border-b-0 lg:px-6 lg:py-6">
          <div className="flex flex-col gap-4">
            <div>
              <p className="text-xs font-semibold tracking-[0.18em] text-emerald-700 uppercase">
                LDK
              </p>
              <h1 className="mt-1 text-xl font-semibold text-zinc-950">Athlete AI Coach</h1>
            </div>

            <nav aria-label="Main navigation" className="flex gap-2 overflow-x-auto lg:flex-col">
              {navigationItems.map((item) => {
                const isActive = pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`rounded-lg px-3 py-2 text-sm font-medium whitespace-nowrap transition ${
                      isActive
                        ? "bg-emerald-700 text-white"
                        : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-950"
                    }`}
                    aria-current={isActive ? "page" : undefined}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-5 lg:mt-8">
            <p className="mb-2 text-xs font-medium text-zinc-500">Backend status</p>
            <StatusBadge status={backendStatus} />
          </div>
        </aside>

        <main className="flex-1 px-5 py-6 sm:px-8 lg:px-10 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
