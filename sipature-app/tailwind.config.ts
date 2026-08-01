import type { Config } from "tailwindcss";

/**
 * Token warna mengacu pada palet tervalidasi (dataviz skill).
 * Semua nilai dideklarasikan sebagai CSS custom property di globals.css
 * agar light/dark berganti di satu tempat.
 */
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "var(--surface-1)",
        "surface-2": "var(--surface-2)",
        plane: "var(--plane)",
        ink: "var(--text-primary)",
        "ink-2": "var(--text-secondary)",
        muted: "var(--text-muted)",
        hairline: "var(--hairline)",
        grid: "var(--gridline)",
        // status sinyal — tetap, tidak ikut tema
        good: "var(--status-good)",
        warning: "var(--status-warning)",
        serious: "var(--status-serious)",
        critical: "var(--status-critical)",
        // kategorikal
        s1: "var(--series-1)",
        s2: "var(--series-2)",
        s3: "var(--series-3)",
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      borderRadius: { card: "10px" },
    },
  },
  plugins: [],
};

export default config;
