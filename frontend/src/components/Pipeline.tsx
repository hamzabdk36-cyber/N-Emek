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
/**
 * Bir bagin kanit satirlari, asamaya gore gruplanmis.
 *
 * Gruplama sart: cok bolgeli sorgu ayni asamadan bolge basina bir kanit
 * uretiyor. Ayse'nin bagi 4 ayri "Gorsel benzerlik modeli" satiri
 * dogurmustu ve hepsi neredeyse ayni cumleyi yaziyordu; buyuk bir
 * korpusta bu 11'e cikar. Juri bu ekranda "hangi asama ne buldu"
 * sorusunun cevabini ariyor - satir sayisini degil.
 *
 * Ozet satirda en fazla iki farkli aciklama gosterilir; gerisi sayiya
 * doner. Hicbir olcum atilmaz, hepsi acilir panelde duruyor.
 */
type Detail = Record<string, unknown>;

function rowLabel(row: EvidenceRow | EvidenceItem): string {
  return (
    (row as EvidenceRow).label ??
    STAGE_META[row.stage as string]?.title ??
    String(row.stage)
  );
}

function rowDetail(row: EvidenceRow | EvidenceItem): Detail {
  return (
    (row as EvidenceRow).detay ??
    Object.fromEntries(
      Object.entries(row).filter(
        ([k]) => !["stage", "found", "matched", "aciklama"].includes(k),
      ),
    )
  );
}

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

  // Asamaya gore grupla, ilk gorulme sirasini koru.
  const groups: { key: string; label: string; items: (EvidenceRow | EvidenceItem)[] }[] = [];
  for (const row of visible) {
    const key = String(row.stage ?? rowLabel(row));
    const found = groups.find((g) => g.key === key);
    if (found) found.items.push(row);
    else groups.push({ key, label: rowLabel(row), items: [row] });
  }

  return (
    <ul className="space-y-1.5">
      {groups.map((group, i) => {
        const aciklamalar = [
          ...new Set(
            group.items
              .map((r) => r.aciklama)
              .filter((a): a is string => Boolean(a)),
          ),
        ];
        const gosterilen = aciklamalar.slice(0, 2);
        const gizli = aciklamalar.length - gosterilen.length;
        const detaylar = group.items
          .map(rowDetail)
          .filter((d) => Object.keys(d).length > 0);
        const hasDetail = detaylar.length > 0;

        return (
          <li
            key={group.key}
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
                <span className="flex flex-wrap items-center gap-2">
                  <span className="text-[12.5px] font-medium text-[var(--color-ink)]">
                    {group.label}
                  </span>
                  {group.items.length > 1 && (
                    <span className="num rounded border border-[var(--color-line)] px-1.5 py-px text-[10.5px] text-[var(--color-ink-3)]">
                      {group.items.length} ölçüm
                    </span>
                  )}
                </span>
                {!compact &&
                  gosterilen.map((a) => (
                    <span
                      key={a}
                      className="mt-0.5 block text-[12px] leading-relaxed text-[var(--color-ink-2)]"
                    >
                      {a}
                    </span>
                  ))}
                {!compact && gizli > 0 && (
                  <span className="mt-0.5 block text-[11.5px] text-[var(--color-ink-3)]">
                    +{gizli} ölçüm daha
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
              <div className="fade-in border-t border-[var(--color-line-soft)]">
                {detaylar.map((detail, j) => (
                  <dl
                    key={j}
                    className="grid grid-cols-2 gap-x-4 gap-y-1 px-3 py-2.5 not-first:border-t not-first:border-[var(--color-line-soft)] sm:grid-cols-3"
                  >
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
                ))}
              </div>
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
