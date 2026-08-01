"use client";

/**
 * Peta sungguhan berbasis Leaflet + tile raster gratis.
 *
 * Kenapa Leaflet raster, bukan MapLibre vektor:
 *   Tile vektor menuntut WebGL plus tiga jenis permintaan tambahan
 *   (style JSON, glyph font, sprite). Raster hanya PNG. Di ruang lockdown
 *   dengan perangkat dan jaringan yang tidak terjamin, lebih sedikit titik
 *   gagal lebih berharga daripada zoom yang mulus.
 *
 * Penyedia tile — semuanya gratis dan tanpa API key:
 *   · CARTO Positron / Dark Matter  — basemap muted, sengaja dipilih agar
 *     tidak berebut perhatian dengan warna data di atasnya.
 *   · Esri World Imagery            — citra satelit.
 * Atribusi keduanya WAJIB tampil dan sudah dipasang di bawah.
 *
 * Komponen ini HANYA dimuat lewat next/dynamic dengan ssr:false — Leaflet
 * menyentuh `window` saat modul dievaluasi.
 */

import { useEffect, useMemo, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import { levelOf, score } from "@/lib/format";
import { ASPECT_LABEL } from "@/lib/format";
import type { Basemap, MapPoint } from "./TobaMap";

/** Ambil nilai token CSS. Menjaga satu sumber kebenaran di globals.css. */
function readVar(name: string, fallback: string): string {
  if (typeof window === "undefined") return fallback;
  const v = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return v || fallback;
}

const TILES: Record<
  Exclude<Basemap, "auto">,
  { url: string; attribution: string; maxZoom: number }
> = {
  terang: {
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
  },
  gelap: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
  },
  satelit: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution:
      "Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics",
    maxZoom: 18,
  },
};

/** Radius marker menurut jumlah ulasan — akar kuadrat agar tidak berlebihan. */
function radiusFor(n: number, maxN: number): number {
  if (maxN <= 0) return 5;
  return 4 + 7 * Math.sqrt(Math.min(n, maxN) / maxN);
}

export interface LeafletMapProps {
  points: MapPoint[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  basemap: Basemap;
  /** Dipanggil bila tile gagal berulang kali → pembungkus beralih ke SVG luring. */
  onTileFailure?: () => void;
}

export default function LeafletMap({
  points,
  selectedId,
  onSelect,
  basemap,
  onTileFailure,
}: LeafletMapProps) {
  const boxRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const tileRef = useRef<L.TileLayer | null>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);
  const highlightRef = useRef<L.CircleMarker | null>(null);
  /**
   * SATU renderer canvas dipakai bersama seluruh marker. Membuat L.canvas()
   * di dalam perulangan akan melahirkan ratusan elemen canvas bertumpuk —
   * berat dan menyebabkan marker gagal tergambar.
   */
  const rendererRef = useRef<L.Canvas | null>(null);
  const errorsRef = useRef(0);
  const notifiedRef = useRef(false);
  const fittedRef = useRef(false);

  // Handler terbaru disimpan di ref agar efek peta tidak perlu dibuat ulang.
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;
  const failRef = useRef(onTileFailure);
  failRef.current = onTileFailure;

  /** Mode efektif: 'auto' mengikuti tema dokumen. */
  const resolveMode = (): Exclude<Basemap, "auto"> => {
    if (basemap !== "auto") return basemap;
    if (typeof window === "undefined") return "terang";
    const stamped = document.documentElement.getAttribute("data-theme");
    if (stamped === "dark") return "gelap";
    if (stamped === "light") return "terang";
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "gelap"
      : "terang";
  };

  /* ------------------------------------------------------- inisialisasi */
  useEffect(() => {
    if (mapRef.current || !boxRef.current) return;

    const map = L.map(boxRef.current, {
      center: [2.6, 98.85],
      zoom: 9,
      minZoom: 7,
      maxZoom: 18,
      zoomControl: true,
      attributionControl: true,
      // Canvas jauh lebih ringan untuk ratusan marker daripada SVG per-elemen.
      preferCanvas: true,
      worldCopyJump: false,
    });

    map.attributionControl.setPrefix(
      '<a href="https://leafletjs.com">Leaflet</a>',
    );

    rendererRef.current = L.canvas({ padding: 0.5 });
    rendererRef.current.addTo(map);
    markersRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
      tileRef.current = null;
      markersRef.current = null;
      highlightRef.current = null;
      rendererRef.current = null;
      fittedRef.current = false;
    };
  }, []);

  /* ------------------------------------------------------------- basemap */
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const mode = resolveMode();
    const spec = TILES[mode];

    if (tileRef.current) {
      map.removeLayer(tileRef.current);
      tileRef.current = null;
    }

    const layer = L.tileLayer(spec.url, {
      attribution: spec.attribution,
      maxZoom: spec.maxZoom,
      detectRetina: true,
      crossOrigin: true,
      // Subdomain hanya berlaku untuk CARTO; Esri mengabaikannya.
      subdomains: mode === "satelit" ? [""] : ["a", "b", "c", "d"],
    });

    layer.on("tileerror", () => {
      errorsRef.current += 1;
      // Ambang 6: satu-dua tile gagal itu wajar; enam berarti jaringan mati.
      if (errorsRef.current >= 6 && !notifiedRef.current) {
        notifiedRef.current = true;
        failRef.current?.();
      }
    });
    layer.on("tileload", () => {
      errorsRef.current = 0;
    });

    layer.addTo(map);
    layer.bringToBack();
    tileRef.current = layer;
    // resolveMode membaca DOM, bukan state — deps sengaja hanya basemap.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [basemap]);

  /* -------------------------------- ikut berubah saat tema diganti (auto) */
  useEffect(() => {
    if (basemap !== "auto" || typeof window === "undefined") return;

    const swap = () => {
      const map = mapRef.current;
      if (!map) return;
      const spec = TILES[resolveMode()];
      if (tileRef.current) {
        tileRef.current.setUrl(spec.url);
        tileRef.current.options.attribution = spec.attribution;
      }
    };

    const obs = new MutationObserver(swap);
    obs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", swap);

    return () => {
      obs.disconnect();
      mq.removeEventListener("change", swap);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [basemap]);

  /* ------------------------------------------------------------- marker */
  const maxReviews = useMemo(
    () => points.reduce((m, p) => Math.max(m, p.allReviewCount), 0),
    [points],
  );

  useEffect(() => {
    const map = mapRef.current;
    const group = markersRef.current;
    if (!map || !group) return;

    group.clearLayers();
    highlightRef.current = null;

    // Friksi rendah digambar dulu, tinggi terakhir → yang genting tampak di atas.
    const ordered = [...points].sort(
      (a, b) => (a.priorityScore ?? -1) - (b.priorityScore ?? -1),
    );

    for (const p of ordered) {
      const lvl = levelOf(p.priority);
      const weak = lvl.key === "none";
      const radius = weak ? 4 : radiusFor(p.allReviewCount, maxReviews);
      const symbolSize = Math.max(12, Math.round(radius * 2));

      const marker = L.marker([p.lat, p.lon], {
        icon: L.divIcon({
          className: "mh-map-marker",
          html: `<span class="mh-map-symbol${weak ? " is-weak" : ""}" style="--marker-color:${lvl.colorVar};--marker-size:${symbolSize}px" aria-hidden="true">${lvl.icon}</span>`,
          // Kotak transparan 30 px memberi sasaran klik yang nyaman tanpa
          // mengubah ukuran simbol yang mengodekan jumlah review.
          iconSize: [30, 30],
          iconAnchor: [15, 15],
          tooltipAnchor: [0, -12],
        }),
        keyboard: true,
        riseOnHover: true,
        zIndexOffset: Math.round((p.priorityScore ?? -1) * 10),
        bubblingMouseEvents: false,
      });

      const aspects = p.topAspects
        .slice(0, 3)
        .map((a) => ASPECT_LABEL[a])
        .join(" · ");

      // Tooltip memuat ikon + label tingkat: warna tidak pernah sendirian.
      marker.bindTooltip(
        `<div class="mh-tip">
           <strong>${escapeHtml(p.name)}</strong>
           <div class="mh-tip-row"><span aria-hidden>${lvl.icon}</span> ${lvl.label}
             · <span class="tabular">${score(p.priorityScore)}</span></div>
           <div class="mh-tip-sub">${p.kabupaten} · ${p.allReviewCount} review bersih${
             p.rank !== null ? ` · prioritas #${p.rank}` : ""
           }</div>
           ${aspects ? `<div class="mh-tip-sub">${escapeHtml(aspects)}</div>` : ""}
         </div>`,
        {
          direction: "top",
          offset: [0, -2],
          opacity: 1,
          className: "mh-tooltip",
        },
      );

      marker.on("click", () => selectRef.current?.(p.id));
      marker.on("keypress", () => selectRef.current?.(p.id));
      group.addLayer(marker);
    }

    // Sekali saja: pas-kan tampilan ke seluruh titik.
    if (!fittedRef.current && points.length > 0) {
      const b = L.latLngBounds(
        points.map((p) => [p.lat, p.lon] as [number, number]),
      );
      map.fitBounds(b, { padding: [28, 28], maxZoom: 11 });
      fittedRef.current = true;
    }
  }, [points, maxReviews]);

  /* --------------------------------------------------------- penyorotan */
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (highlightRef.current) {
      map.removeLayer(highlightRef.current);
      highlightRef.current = null;
    }
    if (!selectedId) return;

    const p = points.find((x) => x.id === selectedId);
    if (!p) return;

    const ring = L.circleMarker([p.lat, p.lon], {
      renderer: rendererRef.current ?? undefined,
      radius: radiusFor(p.allReviewCount, maxReviews) + 7,
      color: readVar("--series-1", "#2a78d6"),
      weight: 2.5,
      opacity: 1,
      fill: false,
      interactive: false,
    }).addTo(map);

    highlightRef.current = ring;
    map.panInside([p.lat, p.lon], { padding: [40, 40] });
  }, [selectedId, points, maxReviews]);

  return (
    <div
      ref={boxRef}
      className="h-full w-full"
      role="application"
      aria-label="Peta interaktif sinyal prioritas destinasi kawasan Danau Toba"
    />
  );
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
