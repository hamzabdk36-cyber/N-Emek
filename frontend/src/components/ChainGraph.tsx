/**
 * Atif zinciri gorunumu (DAG).
 *
 * Harici bir grafik kutuphanesi yerine dogrudan SVG: dugum sayisi
 * kucuk (zincir en fazla 5 derinlik), yerlesim katmanli ve
 * ongorulebilir, ve tema renklerini birebir kontrol edebiliyoruz.
 *
 * Yerlesim: derinlik = satir. Yaprak (yayinlanan icerik) en altta,
 * kokene dogru yukari cikilir. Okun yonu turetme yonudur: kaynak ->
 * turev.
 *
 * Cizim sirasi onemli - ilk surumdeki hata buradaydi
 * -----------------------------------------------------------------
 * Once her kenar kendi <g>'si icinde "cizgi, sonra rozet" olarak
 * ciziliyordu. Tek kenarda dogru gorunuyor, birden fazla kenarda
 * bozuluyor: bir sonraki kenarin cizgisi, onceki kenarin rozetinin
 * *ustune* biniyor. Demo zincirinde uc dugum de tek sutunda oldugu
 * icin uc kenar da ayni x'te dikey cizgiydi ve en son cizilen kenar
 * diger ikisinin yuzdelerinin tam ortasindan geciyordu.
 *
 * Cozum, kenar basina degil tum grafik icin uc katman:
 *   1) butun cizgiler  2) butun dugumler  3) butun rozetler
 * Boylece hicbir cizgi bir rozetin ustune dusemez ve hicbir rozet bir
 * dugum kutusunun altinda kalmaz.
 *
 * Bir satirdan fazlasini atlayan kenarlar (A -> C, arada B varken)
 * dumduz cizilirse aradaki dugum kutusunun icinden gecer. Onlari sag
 * koridora cikarip her birine kendi seridini veriyoruz.
 */
import type { ChainEdgeView, ChainNodeView } from "../api";

const NODE_W = 196;
const NODE_H = 68;
const GAP_X = 32;
const GAP_Y = 88;
const PAD = 18;
/** Atlama kenarlarinin dolastigi sag koridorda serit genisligi. */
const LANE_W = 30;
/** Koridora cikis / girisin dikey payi. */
const LANE_EASE = 30;

const STATUS_STROKE: Record<string, string> = {
  confirmed: "var(--color-verify)",
  proposed: "var(--color-caution)",
  disputed: "var(--color-alert)",
  rejected: "var(--color-ink-3)",
};

type Point = { x: number; y: number };

type EdgeLayout = {
  edge: ChainEdgeView;
  stroke: string;
  path: string;
  label: string;
  labelAt: Point;
};

export function ChainGraph({
  nodes,
  edges,
  selectedId,
  onSelect,
}: {
  nodes: ChainNodeView[];
  edges: ChainEdgeView[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
}) {
  if (nodes.length === 0) return null;

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

  // Serit araligi rozet genisligine gore: sabit 30px'te "ölçülemedi"
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
  rows.forEach((row, rowIndex) => {
    const rowWidth = row.length * NODE_W + (row.length - 1) * GAP_X;
    const startX = PAD + (bodyW - rowWidth) / 2;
    row.forEach((node, i) => {
      pos.set(node.id, {
        x: startX + i * (NODE_W + GAP_X),
        y: PAD + rowIndex * (NODE_H + GAP_Y),
      });
    });
  });

  const laid: EdgeLayout[] = [];
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
    if (lane == null) {
      // Komsu satirlar: yumusak bir S, rozet tam ortada.
      const midY = (y1 + y2) / 2;
      laid.push({
        edge,
        stroke,
        label,
        path: `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`,
        labelAt: { x: (x1 + x2) / 2, y: midY },
      });
    } else {
      // Atlama kenari: sag koridordaki kendi seridine cikar, iner,
      // hedefin ustunden geri girer. Rozet dikey parcanin ortasinda.
      const lx = laneX(lane);
      const top = y1 + LANE_EASE;
      const bottom = y2 - LANE_EASE;
      laid.push({
        edge,
        stroke,
        label,
        path:
          `M ${x1} ${y1} C ${x1} ${y1 + 16}, ${lx} ${y1 + 4}, ${lx} ${top} ` +
          `L ${lx} ${bottom} ` +
          `C ${lx} ${y2 - 4}, ${x2} ${y2 - 16}, ${x2} ${y2}`,
        labelAt: { x: lx, y: (top + bottom) / 2 },
      });
    }
  }

  return (
    <div className="overflow-x-auto">
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="mx-auto block"
        role="img"
        aria-label="İçerik atıf zinciri"
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
        </defs>

        {/* 1. katman — baglar */}
        <g fill="none">
          {laid.map(({ edge, stroke, path }) => (
            <path
              key={edge.id}
              d={path}
              style={{ color: stroke }}
              stroke={stroke}
              strokeWidth={1.5}
              strokeLinecap="round"
              strokeDasharray={edge.status === "proposed" ? "5 4" : undefined}
              markerEnd="url(#arrow)"
              opacity={edge.status === "rejected" ? 0.35 : 0.85}
            />
          ))}
        </g>

        {/* 2. katman — dugumler */}
        {nodes.map((node) => {
          const p = pos.get(node.id)!;
          const selected = selectedId === node.id;
          const isLeaf = node.role === "leaf";
          return (
            <g
              key={node.id}
              transform={`translate(${p.x} ${p.y})`}
              onClick={() => onSelect?.(node.id)}
              style={{ cursor: onSelect ? "pointer" : "default" }}
            >
              <rect
                width={NODE_W}
                height={NODE_H}
                rx={10}
                fill="var(--color-surface-2)"
                stroke={selected ? node.accent : "var(--color-line)"}
                strokeWidth={selected ? 2 : 1}
                strokeDasharray={node.contributes === false ? "4 3" : undefined}
                opacity={node.contributes === false ? 0.72 : 1}
              />
              <rect
                width={4}
                height={NODE_H}
                rx={2}
                fill={node.accent}
                opacity={node.contributes === false ? 0.4 : 1}
              />
              <text x={18} y={25} fontSize={13} fill="var(--color-ink)" fontWeight={600}>
                {truncate(node.title || "(başlıksız)", 22)}
              </text>
              <text x={18} y={42} fontSize={11.5} fill="var(--color-ink-2)">
                {truncate(node.owner, 24)}
              </text>
              <text
                x={18}
                y={58}
                fontSize={10}
                fill="var(--color-ink-3)"
                fontFamily="var(--font-mono)"
                letterSpacing="0.04em"
              >
                {isLeaf
                  ? "YAYINLANAN"
                  : node.contributes === false
                    ? "ARA HALKA · PAY YOK"
                    : `${node.depth} ADIM GERİDE`}
              </text>
              {node.contributes === false && (
                <title>
                  Zincirde yer alıyor ama kendi kattığı alan ödeme eşiğinin altında.
                </title>
              )}
            </g>
          );
        })}

        {/* 3. katman — kapsama rozetleri; her seyin ustunde */}
        {laid.map(({ edge, stroke, label, labelAt }) => {
          const w = badgeWidth(label);
          return (
            <g key={edge.id} style={{ color: stroke }}>
              <rect
                x={labelAt.x - w / 2}
                y={labelAt.y - 10}
                width={w}
                height={20}
                rx={10}
                fill="var(--color-surface)"
                stroke={stroke}
                strokeOpacity={0.45}
              />
              <text
                x={labelAt.x}
                y={labelAt.y + 4}
                textAnchor="middle"
                fontSize={11}
                fill={stroke}
                fontFamily="var(--font-mono)"
              >
                {label}
              </text>
              <title>
                {`${edge.stage_label} · güven ${edge.confidence.score.toFixed(2)} · kullanılan alan ${label}`}
              </title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function coverageLabel(edge: ChainEdgeView) {
  return edge.visual_coverage != null
    ? `%${(edge.visual_coverage * 100).toFixed(0)}`
    : "ölçülemedi";
}

/** Rozet metne gore genisler. Sabit 60px'te "ölçülemedi" tasip cizgiye biniyordu. */
function badgeWidth(text: string) {
  return Math.max(42, Math.round(text.length * 6.7) + 18);
}

function truncate(text: string, max: number) {
  return text.length > max ? text.slice(0, max - 1) + "…" : text;
}
