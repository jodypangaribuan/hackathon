"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const LINKS = [
  { href: "/", label: "Peta Friksi" },
  { href: "/umkm", label: "Peluang UMKM" },
  { href: "/analyzer", label: "Live Analyzer" },
  { href: "/metode", label: "Metode" },
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
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
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
      {theme === "dark" ? "☀" : "☾"}
    </button>
  );
}

export default function Nav() {
  const pathname = usePathname();

  return (
    <header
      className="sticky top-0 z-30 border-b backdrop-blur"
      style={{ borderColor: "var(--hairline)", background: "color-mix(in srgb, var(--plane) 88%, transparent)" }}
    >
      <div className="mx-auto flex h-14 max-w-[1400px] items-center gap-6 px-4">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="text-[15px] font-semibold tracking-tight">MARTAHUTA</span>
          <span className="hidden text-[11px] text-muted sm:inline">
            Toba Retention Intelligence
          </span>
        </Link>

        <nav className="flex items-center gap-1 text-[13px]">
          {LINKS.map((l) => {
            const active = l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className="rounded-md px-2.5 py-1.5 transition-colors"
                style={{
                  color: active ? "var(--text-primary)" : "var(--text-secondary)",
                  background: active ? "var(--surface-2)" : "transparent",
                  fontWeight: active ? 600 : 400,
                }}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <span
            className="hidden rounded-md border px-2 py-1 text-[11px] text-muted lg:inline"
            style={{ borderColor: "var(--hairline)" }}
            title="Angka berasal dari baseline keyword+rating, bukan model IndoBERT terlatih."
          >
            Data contoh · baseline
          </span>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
