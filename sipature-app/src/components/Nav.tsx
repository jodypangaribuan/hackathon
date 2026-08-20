"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  BrainCircuit,
  Compass,
  FlaskConical,
  Layers,
  ListChecks,
  Moon,
  Sun,
} from "lucide-react";

const LINKS = [
  { href: "/", label: "Overview", icon: BarChart3 },
  { href: "/destinasi", label: "Destinasi", icon: Compass },
  { href: "/intervensi", label: "Intervensi", icon: ListChecks },
  { href: "/umkm", label: "Rekomendasi", icon: Layers },
  { href: "/simulator", label: "Simulator", icon: FlaskConical },
  { href: "/analyzer", label: "Analisis Review", icon: BrainCircuit },
  { href: "/metode", label: "Model", icon: Activity },
];

function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark" | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("mh-theme");
    if (stored === "light" || stored === "dark") {
      document.documentElement.setAttribute("data-theme", stored);
      setTheme(stored);
    }
  }, []);

  function toggle() {
    const current =
      theme ??
      (window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    window.localStorage.setItem("mh-theme", next);
    setTheme(next);
  }

  return (
    <button
      onClick={toggle}
      className="rounded-md border px-2 py-1 text-[12px] text-ink-2 transition-colors hover:text-ink"
      style={{ borderColor: "var(--hairline)" }}
      aria-label="Ganti tema terang/gelap"
    >
      {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
    </button>
  );
}

export default function Nav() {
  const pathname = usePathname();

  return (
    <header
      className="sticky top-0 z-30 border-b backdrop-blur"
      style={{
        borderColor: "var(--hairline)",
        background: "color-mix(in srgb, var(--plane) 88%, transparent)",
      }}
    >
      <div className="mx-auto flex h-14 max-w-[1400px] items-center gap-3 px-4 sm:gap-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-[15px] font-semibold tracking-tight">
            SIPATURE
          </span>
          <span className="hidden text-[11px] text-muted sm:inline">
            Tourism Quality Intelligence
          </span>
        </Link>

        <nav className="thin-scroll flex min-w-0 flex-1 items-center gap-1 overflow-x-auto text-[13px]">
          {LINKS.map((l) => {
            const active =
              l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className="shrink-0 rounded-md px-2.5 py-1.5 transition-colors"
                style={{
                  color: active
                    ? "var(--text-primary)"
                    : "var(--text-secondary)",
                  background: active ? "var(--surface-2)" : "transparent",
                  fontWeight: active ? 600 : 400,
                }}
              >
                <span className="inline-flex items-center gap-1.5">
                  <l.icon size={13} />
                  {l.label}
                </span>
              </Link>
            );
          })}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <span
            className="hidden rounded-md border px-2 py-1 text-[11px] text-muted lg:inline"
            style={{ borderColor: "var(--hairline)" }}
            title="Sistem Berjalan Mandiri — DGX B200 Production"
          >
            Production v1.0.4
          </span>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
