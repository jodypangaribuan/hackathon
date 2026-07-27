/**
 * Simulasi intervensi: "bila keluhan X diselesaikan, indeks friksi jadi berapa?"
 *
 * Fungsi MURNI — tidak mengimpor data besar, sehingga aman dipakai di client
 * component tanpa menyeret places.json (892 KB) ke dalam bundle browser.
 * Tangga peringkat dikirim sebagai prop dari server component.
 */
import type { AspectKey, Place, SimulateResult } from "./types";
import { ASPECT_LABEL } from "./format";

/**
 * Daftar frictionScore seluruh tempat berperingkat, urut menurun.
 * Dipakai untuk menghitung ulang posisi peringkat setelah perbaikan.
 */
export type RankLadder = number[];

export function buildRankLadder(scores: number[]): RankLadder {
  return [...scores].sort((a, b) => b - a);
}

/** Peringkat 1-indexed dari sebuah skor pada tangga peringkat. */
export function rankForScore(score: number, ladder: RankLadder): number {
  let i = 0;
  while (i < ladder.length && ladder[i] > score) i++;
  return i + 1;
}

/**
 * Hitung ulang indeks setelah sejumlah aspek "diperbaiki".
 *
 * Model perbaikan sengaja dibuat konservatif dan mudah dijelaskan:
 * kontribusi aspek yang diperbaiki dihapus seluruhnya. Ini adalah batas ATAS
 * dari perbaikan yang mungkin — bukan prediksi. Peringatan kausalitas pada
 * `caveat` wajib ikut ditampilkan.
 */
export function simulateFixes(
  place: Place,
  fixes: AspectKey[],
  ladder: RankLadder,
): SimulateResult {
  const fixSet = new Set(fixes);

  const removed = place.aspects
    .filter((a) => fixSet.has(a.aspect) && a.frictionContrib > 0)
    .map((a) => ({
      aspect: a.aspect,
      label: ASPECT_LABEL[a.aspect],
      delta: Math.round(a.frictionContrib * 100 * 10) / 10,
    }))
    .sort((x, y) => y.delta - x.delta);

  const removedTotal = removed.reduce((s, r) => s + r.delta, 0);
  const afterScore = Math.max(0, Math.round((place.frictionScore - removedTotal) * 10) / 10);

  // Tempat itu sendiri dikeluarkan dari tangga sebelum peringkat baru dihitung,
  // supaya ia tidak dibandingkan dengan dirinya yang lama.
  const ladderWithout = [...ladder];
  const own = ladderWithout.indexOf(place.frictionScore);
  if (own >= 0) ladderWithout.splice(own, 1);

  const canRank = place.rank !== null;

  return {
    placeId: place.id,
    placeName: place.name,
    before: { score: place.frictionScore, rank: place.rank },
    after: {
      score: afterScore,
      rank: canRank ? rankForScore(afterScore, ladderWithout) : null,
    },
    removed,
    caveat:
      "Proyeksi berbasis asosiasi historis pada data ulasan, bukan jaminan kausal. " +
      "Angka ini adalah batas atas: seluruh kontribusi aspek dianggap hilang sepenuhnya. " +
      "Uji kausal memerlukan pilot terkendali di satu kecamatan.",
  };
}
