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
 */
import type { ChainEdgeView, ChainNodeView } from "../api";

const NODE_W = 168;
const NODE_H = 62;
const GAP_X = 28;
const GAP_Y = 74;
const PAD = 16;

const STATUS_STROKE: Record<string, string> = {
  confirmed: "var(--color-verify)",
  proposed: "var(--color-caution)",
  disputed: "var(--color-alert)",
  rejected: "var(--color-ink-3)",
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
  const widest = Math.max(...rows.map((r) => r.length));

  const width = PAD * 2 + widest * NODE_W + (widest - 1) * GAP_X;
  const height = PAD * 2 + rows.length * NODE_H + (rows.length - 1) * GAP_Y;

  const pos = new Map<string, { x: number; y: number }>();
  rows.forEach((row, rowIndex) => {
    const rowWidth = row.length * NODE_W + (row.length - 1) * GAP_X;
    const startX = (width - rowWidth) / 2;
    row.forEach((node, i) => {
      pos.set(node.id, {
        x: startX + i * (NODE_W + GAP_X),
        y: PAD + rowIndex * (NODE_H + GAP_Y),
      });
    });
  });

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

        {edges.map((edge) => {
          const from = pos.get(edge.from);
          const to = pos.get(edge.to);
          if (!from || !to) return null;
          const x1 = from.x + NODE_W / 2;
          const y1 = from.y + NODE_H;
          const x2 = to.x + NODE_W / 2;
          const y2 = to.y;
          const midY = (y1 + y2) / 2;
          const stroke = STATUS_STROKE[edge.status] ?? "var(--color-ink-3)";
          const coverage =
            edge.visual_coverage != null
              ? `%${(edge.visual_coverage * 100).toFixed(0)}`
              : "ölçülemedi";
          return (
            <g key={edge.id} style={{ color: stroke }}>
              <path
                d={`M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`}
                fill="none"
                stroke={stroke}
                strokeWidth={1.5}
                strokeDasharray={edge.status === "proposed" ? "5 4" : undefined}
                markerEnd="url(#arrow)"
                opacity={0.85}
              />
              <rect
                x={(x1 + x2) / 2 - 30}
                y={midY - 10}
                width={60}
                height={19}
                rx={5}
                fill="var(--color-surface)"
                stroke={stroke}
                strokeOpacity={0.4}
              />
              <text
                x={(x1 + x2) / 2}
                y={midY + 3}
                textAnchor="middle"
                fontSize={11}
                fill={stroke}
                fontFamily="var(--font-mono)"
              >
                {coverage}
              </text>
              <title>
                {`${edge.stage_label} · güven ${edge.confidence.score.toFixed(2)} · kullanılan alan ${coverage}`}
              </title>
            </g>
          );
        })}

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
              />
              <rect width={4} height={NODE_H} rx={2} fill={node.accent} />
              <text x={16} y={23} fontSize={12.5} fill="var(--color-ink)" fontWeight={600}>
                {truncate(node.title || "(başlıksız)", 20)}
              </text>
              <text x={16} y={40} fontSize={11.5} fill="var(--color-ink-2)">
                {truncate(node.owner, 22)}
              </text>
              <text
                x={16}
                y={54}
                fontSize={10.5}
                fill="var(--color-ink-3)"
                fontFamily="var(--font-mono)"
              >
                {isLeaf ? "yayınlanan içerik" : `zincirde ${node.depth} adım geride`}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function truncate(text: string, max: number) {
  return text.length > max ? text.slice(0, max - 1) + "…" : text;
}
