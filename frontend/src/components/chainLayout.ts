/**
 * Atif zinciri yerlesim hesabi - saf fonksiyon.
 *
 * Neden bilesenden ayri
 * ---------------------
 * 10 Agustos'taki rozet-cizgi cakismasi ekranda duran ama kod okunarak
 * bulunamayan bir hataydi; ancak takim sikayet edince goruldu. Yerlesim
 * DOM'dan bagimsiz saf bir fonksiyon oldugunda "hicbir rozet hicbir
 * dugum kutusuyla kesismiyor" iddiasi dogrudan sinanabiliyor
 * (`chainLayout.test.ts`).
 *
 * Yerlesim: derinlik = satir. Yaprak (yayinlanan icerik) en altta,
 * kokene dogru yukari cikilir. Okun yonu turetme yonudur: kaynak ->
 * turev.
 *
 * Bir satirdan fazlasini atlayan kenarlar (A -> C, arada B varken)
 * dumduz cizilirse aradaki dugum kutusunun icinden gecer. Onlari sag
 * koridora cikarip her birine kendi seridini veriyoruz.
 */
import type { ChainEdgeView, ChainNodeView } from "../api";

export const NODE_W = 196;
export const NODE_H = 68;
export const GAP_X = 32;
export const GAP_Y = 88;
export const PAD = 18;
/** Atlama kenarlarinin dolastigi sag koridorda serit genisligi. */
export const LANE_W = 30;
/** Koridora cikis / girisin dikey payi. */
export const LANE_EASE = 30;
/** Rozet yuksekligi; cizimdeki <rect height> ile ayni olmali. */
export const BADGE_H = 20;

const STATUS_STROKE: Record<string, string> = {
  confirmed: "var(--color-verify)",
  proposed: "var(--color-caution)",
  disputed: "var(--color-alert)",
  rejected: "var(--color-ink-3)",
};

export type Point = { x: number; y: number };

/** Sol ust kose + olculer. Kesisim testleri bunun uzerinden yapiliyor. */
export type Rect = { x: number; y: number; w: number; h: number };

export type NodeLayout = {
  node: ChainNodeView;
  /** Dugum kutusunun sol ust kosesi. */
  at: Point;
  box: Rect;
};

export type EdgeLayout = {
  edge: ChainEdgeView;
  stroke: string;
  path: string;
  label: string;
  /** Rozetin merkezi. */
  labelAt: Point;
  /** Rozetin cizilen dikdortgeni. */
  badge: Rect;
  /** Koridora cikan kenarlarda serit numarasi, degilse null. */
  lane: number | null;
};

export type ChainLayout = {
  width: number;
  height: number;
  nodes: NodeLayout[];
  edges: EdgeLayout[];
};

export function chainLayout(
  nodes: ChainNodeView[],
  edges: ChainEdgeView[],
): ChainLayout {
  if (nodes.length === 0) {
    return { width: 0, height: 0, nodes: [], edges: [] };
  }

  // Derinlige gore satirlar; en derin kaynak en ustte.
  const depths = [...new Set(nodes.map((n) => n.depth))].sort((a, b) => b - a);
  const rows = depths.map((d) => nodes.filter((n) => n.depth === d));
  const rowOf = new Map<string, number>();
  rows.forEach((row, i) => row.forEach((n) => rowOf.set(n.id, i)));

  const widest = Math.max(...rows.map((r) => r.length));
  const bodyW = widest * NODE_W + (widest - 1) * GAP_X;

  // Bir satirdan fazlasini atlayan kenarlar koridora cikar. Uzun olan
  // disa dussun ki seritler birbirini kesmesin.
  const skipEdges = edges
    .filter((e) => {
      const a = rowOf.get(e.from);
      const b = rowOf.get(e.to);
      return a != null && b != null && b - a > 1;
    })
    .sort((a, b) => {
      const spanA = rowOf.get(a.to)! - rowOf.get(a.from)!;
      const spanB = rowOf.get(b.to)! - rowOf.get(b.from)!;
      return spanA - spanB;
    });
  const laneOf = new Map(skipEdges.map((e, i) => [e.id, i]));

  // Serit araligi rozet genisligine gore: sabit 30px'te "olculemedi"
  // rozeti sola tasip aradaki dugum kutusunun uzerine biniyordu.
  const laneSlot = Math.max(
    LANE_W,
    ...skipEdges.map((e) => badgeWidth(coverageLabel(e)) + 8),
  );
  const corridorW = skipEdges.length ? 12 + skipEdges.length * laneSlot : 0;
  const laneX = (lane: number) =>
    PAD + bodyW + 12 + lane * laneSlot + laneSlot / 2;
  const width = PAD * 2 + bodyW + corridorW;
  const height = PAD * 2 + rows.length * NODE_H + (rows.length - 1) * GAP_Y;

  const pos = new Map<string, Point>();
  const laidNodes: NodeLayout[] = [];
  rows.forEach((row, rowIndex) => {
    const rowWidth = row.length * NODE_W + (row.length - 1) * GAP_X;
    const startX = PAD + (bodyW - rowWidth) / 2;
    row.forEach((node, i) => {
      const at = {
        x: startX + i * (NODE_W + GAP_X),
        y: PAD + rowIndex * (NODE_H + GAP_Y),
      };
      pos.set(node.id, at);
      laidNodes.push({
        node,
        at,
        box: { x: at.x, y: at.y, w: NODE_W, h: NODE_H },
      });
    });
  });

  const laidEdges: EdgeLayout[] = [];
  for (const edge of edges) {
    const from = pos.get(edge.from);
    const to = pos.get(edge.to);
    if (!from || !to) continue;

    const x1 = from.x + NODE_W / 2;
    const y1 = from.y + NODE_H;
    const x2 = to.x + NODE_W / 2;
    const y2 = to.y;
    const stroke = STATUS_STROKE[edge.status] ?? "var(--color-ink-3)";
    const label = coverageLabel(edge);

    const lane = laneOf.get(edge.id);
    let labelAt: Point;
    let path: string;

    if (lane == null) {
      // Komsu satirlar: yumusak bir S, rozet tam ortada.
      const midY = (y1 + y2) / 2;
      path = `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
      labelAt = { x: (x1 + x2) / 2, y: midY };
    } else {
      // Atlama kenari: sag koridordaki kendi seridine cikar, iner,
      // hedefin ustunden geri girer. Rozet dikey parcanin ortasinda.
      const lx = laneX(lane);
      const top = y1 + LANE_EASE;
      const bottom = y2 - LANE_EASE;
      path =
        `M ${x1} ${y1} C ${x1} ${y1 + 16}, ${lx} ${y1 + 4}, ${lx} ${top} ` +
        `L ${lx} ${bottom} ` +
        `C ${lx} ${y2 - 4}, ${x2} ${y2 - 16}, ${x2} ${y2}`;
      labelAt = { x: lx, y: (top + bottom) / 2 };
    }

    const w = badgeWidth(label);
    laidEdges.push({
      edge,
      stroke,
      label,
      path,
      labelAt,
      badge: {
        x: labelAt.x - w / 2,
        y: labelAt.y - BADGE_H / 2,
        w,
        h: BADGE_H,
      },
      lane: lane ?? null,
    });
  }

  return { width, height, nodes: laidNodes, edges: laidEdges };
}

export function coverageLabel(edge: ChainEdgeView) {
  return edge.visual_coverage != null
    ? `%${(edge.visual_coverage * 100).toFixed(0)}`
    : "ölçülemedi";
}

/** Rozet metne gore genisler. Sabit 60px'te "olculemedi" tasip cizgiye biniyordu. */
export function badgeWidth(text: string) {
  return Math.max(42, Math.round(text.length * 6.7) + 18);
}

/** Iki dikdortgen ortusuyor mu. Sinira degmek kesisme sayilmaz. */
export function overlaps(a: Rect, b: Rect): boolean {
  return (
    a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h
  );
}
