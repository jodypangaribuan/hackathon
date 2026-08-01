import type { LucideProps } from "lucide-react";
import {
  Accessibility,
  Armchair,
  ArrowRight,
  BedDouble,
  Building2,
  Bus,
  Check,
  CircleParking,
  Clock3,
  Coins,
  Info,
  Map,
  ShieldCheck,
  Sparkles,
  Store,
  Trash2,
  TriangleAlert,
  Trees,
  UserRoundCheck,
  Users,
  Utensils,
  Wrench,
} from "lucide-react";
import type { AspectKey } from "@/lib/types";

const ASPECT_ICONS: Record<AspectKey, React.ComponentType<LucideProps>> = {
  cleanliness: Sparkles,
  waste: Trash2,
  sanitation: Accessibility,
  crowding: Users,
  access: Map,
  parking: CircleParking,
  public_facilities: Building2,
  scenery: Trees,
  comfort: Armchair,
  safety: ShieldCheck,
  price_transparency: Coins,
  staff_service: UserRoundCheck,
  maintenance: Wrench,
  opening_hours: Clock3,
};

export function AspectIcon({
  aspect,
  ...props
}: { aspect: AspectKey } & LucideProps) {
  const Icon = ASPECT_ICONS[aspect];
  return <Icon aria-hidden size={15} strokeWidth={1.8} {...props} />;
}

export const AppIcons = {
  ArrowRight,
  BedDouble,
  Bus,
  Check,
  Info,
  Sparkles,
  Store,
  TriangleAlert,
  Utensils,
};
