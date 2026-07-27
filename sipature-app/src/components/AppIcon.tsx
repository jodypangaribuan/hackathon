import type { LucideProps } from "lucide-react";
import {
  Accessibility, ArrowDown, ArrowRight, ArrowUp, BedDouble, Bus, Check,
  CircleParking, Clock3, Coins, Info, Map, MapPin, Minus, ShieldCheck,
  Sparkles, Store, Trash2, TriangleAlert, Trees, Utensils,
} from "lucide-react";
import type { AspectKey, Trend } from "@/lib/types";

const ASPECT_ICONS: Record<AspectKey, React.ComponentType<LucideProps>> = {
  kebersihan: Trash2,
  harga_pungli: Coins,
  toilet_sanitasi: Accessibility,
  parkir: CircleParking,
  akses_jalan: Map,
  ramah_keluarga: Accessibility,
  halal_muslim: Utensils,
  rumah_ibadah: MapPin,
  jam_operasional: Clock3,
  keamanan_sikap: ShieldCheck,
  pemandangan: Trees,
};

export function AspectIcon({ aspect, ...props }: { aspect: AspectKey } & LucideProps) {
  const Icon = ASPECT_ICONS[aspect];
  return <Icon aria-hidden size={15} strokeWidth={1.8} {...props} />;
}

export function TrendIcon({ trend, ...props }: { trend: Trend } & LucideProps) {
  const Icon = trend === "naik" ? ArrowUp : trend === "turun" ? ArrowDown : Minus;
  return <Icon aria-hidden size={13} {...props} />;
}

export const AppIcons = { ArrowRight, BedDouble, Bus, Check, Info, Sparkles, Store, TriangleAlert, Utensils };
