import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="py-24 text-center">
      <p className="text-[40px] font-semibold tracking-tight">404</p>
      <p className="mt-2 text-[13px] text-muted">
        Halaman atau tempat yang dicari tidak ada pada dataset.
      </p>
      <Link
        href="/"
        className="mt-5 inline-block rounded-md border px-4 py-2 text-[13px] font-medium transition-colors hover:bg-surface-2"
        style={{ borderColor: "var(--hairline)" }}
      >
        <span className="inline-flex items-center gap-1.5">
          <ArrowLeft size={14} />
          Kembali ke overview
        </span>
      </Link>
    </div>
  );
}
