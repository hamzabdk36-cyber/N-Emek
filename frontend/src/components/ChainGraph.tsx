/**
 * Atif zinciri gorunumu (DAG).
 *
 * Harici bir grafik kutuphanesi yerine dogrudan SVG: dugum sayisi
 * kucuk (zincir en fazla 5 derinlik), yerlesim katmanli ve
 * ongorulebilir, ve tema renklerini birebir kontrol edebiliyoruz.
 *
 * Yerlesim hesabi burada degil `chainLayout.ts` icinde: saf bir
 * fonksiyon oldugu icin "hicbir rozet hicbir dugum kutusuyla
 * kesismiyor" iddiasi test edilebiliyor. Bu dosya yalnizca cizim.
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
 */
import type { ChainEdgeView, ChainNodeView } from "../api";
import { NODE_H, NODE_W, chainLayout } from "./chainLayout";

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

  const layout = chainLayout(nodes, edges);
  const { width, height } = layout;

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
          {layout.edges.map(({ edge, stroke, path }) => (
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
        {layout.nodes.map(({ node, at }) => {
          const selected = selectedId === node.id;
          const isLeaf = node.role === "leaf";
          return (
            <g
              key={node.id}
              transform={`translate(${at.x} ${at.y})`}
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
        {layout.edges.map(({ edge, stroke, label, labelAt, badge }) => (
          <g key={edge.id} style={{ color: stroke }}>
            <rect
              x={badge.x}
              y={badge.y}
              width={badge.w}
              height={badge.h}
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
        ))}
      </svg>
    </div>
  );
}

function truncate(text: string, max: number) {
  return text.length > max ? text.slice(0, max - 1) + "…" : text;
}
