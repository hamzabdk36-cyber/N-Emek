/**
 * Koken kurtarma hattinin gorsellestirilmesi.
 *
 * Demonun en anlatici ekrani: hangi asamanin ne buldugunu sirasiyla
 * gosterir. "C2PA yok, filigran yok, ama pHash ve geometri buldu"
 * cumlesi burada tek bakista okunur.
 */
import { useState } from "react";
import type { EvidenceItem, EvidenceRow, StageLog } from "../api";
import { Badge } from "./ui";

const STAGE_META: Record<string, { order: number; title: string; note: string }> = {
  c2pa: {
    order: 0,
    title: "İçerik kimliği (C2PA)",
    note: "İmzalı manifest — köken bir tahmin değil, beyandır.",
  },
  exact: {
    order: 1,
    title: "Birebir dosya eşleşmesi",
    note: "SHA-256; bit bit aynı dosyayı yakalar.",
  },
  watermark: {
    order: 2,
    title: "Görünmez filigran",
    note: "Piksellere gömülü kimlik; metadata silinse de kalır.",
  },
  phash: {
    order: 3,
    title: "Algısal parmak izi",
    note: "Yeniden sıkıştırma, ölçekleme ve renk oynamasına dayanıklı.",
  },
  clip: {
    order: 4,
    title: "Görsel benzerlik modeli",
    note: "Ağır düzenleme, kolaj ve filtrede aday üretir.",
  },
  geometry: {
    order: 5,
    title: "Geometrik doğrulama ve alan ölçümü",
    note: "Bağı doğrular ve kullanılan içerik oranını ölçer.",
  },
};

export function StageTimeline({
  stages,
  timings,
}: {
  stages: StageLog[];
  timings?: Record<string, number>;
}) {
  const ordered = [...stages].sort(
    (a, b) => (STAGE_META[a.stage]?.order ?? 99) - (STAGE_META[b.stage]?.order ?? 99),
  );
  const total = timings
    ? Object.values(timings).reduce((sum, v) => sum + v, 0)
    : null;

  return (
    <div>
      <ol className="relative">
        {ordered.map((stage, i) => {
          const meta = STAGE_META[stage.stage];
          const last = i === ordered.length - 1;
          return (
            <li key={stage.stage} className="relative flex gap-3.5 pb-4 last:pb-0">
              {!last && (
                <span
                  className="absolute top-6 bottom-0 left-[9px] w-px bg-[var(--color-line)]"
                  aria-hidden
                />
              )}
              <span
                className={`relative z-10 mt-1 flex h-[19px] w-[19px] shrink-0 items-center justify-center rounded-full border text-[10px] font-bold ${
                  stage.found
                    ? "border-[var(--color-verify)]/50 bg-[var(--color-verify-dim)] text-[var(--color-verify)]"
                    : "border-[var(--color-line)] bg-[var(--color-surface-2)] text-[var(--color-ink-3)]"
                }`}
                aria-hidden
              >
                {stage.found ? "✓" : "–"}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`text-[13px] font-medium ${
                      stage.found
                        ? "text-[var(--color-ink)]"
                        : "text-[var(--color-ink-3)]"
                    }`}
                  >
                    {meta?.title ?? stage.stage}
                  </span>
                  {stage.found ? (
                    <Badge tone="verify">buldu</Badge>
                  ) : (
                    <Badge tone="neutral">sonuç yok</Badge>
                  )}
                  {timings?.[timingKey(stage.stage)] != null && (
                    <span className="num text-[11px] text-[var(--color-ink-3)]">
                      {timings[timingKey(stage.stage)].toFixed(0)} ms
                    </span>
                  )}
                </div>
                <p className="mt-0.5 text-[12px] leading-relaxed text-[var(--color-ink-3)]">
                  {stage.detail || meta?.note}
                </p>
                {stage.aciklama && (
                  <p className="mt-1 text-[12px] leading-relaxed text-[var(--color-ink-2)]">
                    {stage.aciklama}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
      {total != null && (
        <p className="num mt-3 border-t border-[var(--color-line-soft)] pt-3 text-[12px] text-[var(--color-ink-3)]">
          hattın tamamı: {total.toFixed(0)} ms
        </p>
      )}
    </div>
  );
}

function timingKey(stage: string): string {
  if (stage === "phash") return "phash_search";
  if (stage === "clip") return "clip_search";
  return stage;
}

/* -------------------------------------------------------------------------- */
/** Bir bagin kanit satirlari. Her satir bir asamanin ne bulduğunu soyler. */
export function EvidenceList({
  rows,
  compact = false,
}: {
  rows: (EvidenceRow | EvidenceItem)[];
  compact?: boolean;
}) {
  const [open, setOpen] = useState<number | null>(null);
  // Iki kaynaktan gelebiliyor: Emek Karti'ndaki duzenlenmis satirlar
  // (`found`) veya hattin ham kanit sozlukleri (`matched`).
  const visible = rows.filter((row) => {
    const r = row as EvidenceRow & EvidenceItem;
    return r.found ?? r.matched ?? true;
  });
  if (visible.length === 0) {
    return (
      <p className="text-[12px] text-[var(--color-ink-3)]">Kanıt kaydı yok.</p>
    );
  }

  return (
    <ul className="space-y-1.5">
      {visible.map((row, i) => {
        const label =
          (row as EvidenceRow).label ??
          STAGE_META[row.stage as string]?.title ??
          row.stage;
        const detail =
          (row as EvidenceRow).detay ??
          Object.fromEntries(
            Object.entries(row).filter(
              ([k]) => !["stage", "found", "matched", "aciklama"].includes(k),
            ),
          );
        const hasDetail = Object.keys(detail ?? {}).length > 0;
        return (
          <li
            key={i}
            className="rounded-lg border border-[var(--color-line-soft)] bg-[var(--color-surface-2)]/60"
          >
            <button
              type="button"
              onClick={() => hasDetail && setOpen(open === i ? null : i)}
              className="flex w-full items-start gap-2.5 px-3 py-2 text-left"
              aria-expanded={open === i}
            >
              <span className="mt-[3px] text-[var(--color-verify)]" aria-hidden>
                ✓
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[12.5px] font-medium text-[var(--color-ink)]">
                  {label}
                </span>
                {!compact && row.aciklama && (
                  <span className="mt-0.5 block text-[12px] leading-relaxed text-[var(--color-ink-2)]">
                    {row.aciklama}
                  </span>
                )}
              </span>
              {hasDetail && (
                <span className="mt-0.5 text-[11px] text-[var(--color-ink-3)]">
                  {open === i ? "gizle" : "ölçümler"}
                </span>
              )}
            </button>
            {open === i && hasDetail && (
              <dl className="fade-in grid grid-cols-2 gap-x-4 gap-y-1 border-t border-[var(--color-line-soft)] px-3 py-2.5 sm:grid-cols-3">
                {Object.entries(detail).map(([key, value]) => (
                  <div key={key} className="min-w-0">
                    <dt className="truncate text-[10.5px] tracking-wide text-[var(--color-ink-3)] uppercase">
                      {key}
                    </dt>
                    <dd className="num truncate text-[12px] text-[var(--color-ink)]">
                      {formatValue(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "evet" : "hayır";
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }
  return String(value);
}
