/**
 * Koken kurtarma hattinin gorsellestirilmesi.
 *
 * Demonun en anlatici ekrani: hangi asamanin ne buldugunu sirasiyla
 * gosterir. "C2PA yok, filigran yok, ama pHash ve geometri buldu"
 * cumlesi burada tek bakista okunur.
 */
import { useState } from "react";
import { pct, sayi, type EvidenceItem, type EvidenceRow, type StageLog } from "../api";
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
    // Bulgu B5: "algısal" ifadesi sektorde farkli kullanildigi icin
    // kafa karistirdi (KULLANILABILIRLIK-SONUCLARI.md, Gorev 5, K3).
    // Ayni etiket backend'de de degisti (explain.STAGE_LABELS) - ikisi
    // tek kaynaktan gelmiyor ama ayni sozu soylemek zorunda.
    title: "Görüntü parmak izi",
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
  sonucOzeti,
}: {
  stages: StageLog[];
  timings?: Record<string, number>;
  /**
   * Asama listesinin basina, teknik kanit satirlarindan once giren tek
   * cumlelik sonuc (bulgu B5): Kaynak Bul ekraninda bir katilimci
   * "kanit aşamalarını mantıklı" buldu ama onlari sonucun kendisi
   * sandi - asil cevap (kac kaynak bulundu) daha asagidaki ayri
   * panelde, aynı ekranda gec goruluyordu.
   */
  sonucOzeti?: string;
}) {
  const ordered = [...stages].sort(
    (a, b) => (STAGE_META[a.stage]?.order ?? 99) - (STAGE_META[b.stage]?.order ?? 99),
  );
  const total = timings
    ? Object.values(timings).reduce((sum, v) => sum + v, 0)
    : null;

  return (
    <div>
      {sonucOzeti && (
        <p className="mb-4 rounded-lg border border-[var(--color-verify)]/35 bg-[var(--color-verify-dim)]/40 px-3.5 py-2.5 text-[13px] font-medium text-[var(--color-verify)]">
          {sonucOzeti}
        </p>
      )}
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

/**
 * Kanit satirinin basligi.
 *
 * Etiket her zaman backend'den geliyor (`explain.STAGE_LABELS`) - hem
 * Emek Karti hem /verify yolunda. Burada ikinci bir tablo tutmuyoruz:
 * onceki surumde tutuyorduk ve kopya eksikti, `declared` ve
 * `phash_blok` Kaynak Bul ekraninda ham haliyle yaziyordu.
 *
 * `STAGE_META` yalnizca zaman cizelgesinin acilis metnini tasiyor; o,
 * olcumun adi degil arayuzun anlatisi.
 */
function rowLabel(row: EvidenceRow | EvidenceItem): string {
  return (row as EvidenceRow).label ?? String(row.stage);
}

// `label` da disarida: artik /verify yolunda da geliyor ve olcum
// listesinde "LABEL: Geometrik dogrulama" diye gorunurdu.
const OLCUM_DISI = ["stage", "label", "found", "matched", "aciklama"];

function rowDetail(row: EvidenceRow | EvidenceItem): Detail {
  return (
    (row as EvidenceRow).detay ??
    Object.fromEntries(
      Object.entries(row).filter(([k]) => !OLCUM_DISI.includes(k)),
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
                    {Object.entries(detail).map(([key, value]) => {
                      const { etiket, deger, ipucu } = olcumSatiri(key, value);
                      return (
                        <div key={key} className="min-w-0">
                          {/* Etiket artik bir cumle olabiliyor; BUYUK HARF
                              bicimi kaldirildi, okunmuyordu. */}
                          <dt
                            className="truncate text-[10.5px] tracking-wide text-[var(--color-ink-3)]"
                            title={ipucu}
                          >
                            {etiket}
                          </dt>
                          <dd className="num truncate text-[12px] text-[var(--color-ink)]">
                            {deger}
                          </dd>
                        </div>
                      );
                    })}
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

/* -------------------------------------------------------------------------- */
/**
 * Ham olcumlerin Turkce karsiliklari.
 *
 * `BASLARKEN.md` juriye "kanit satirlarina tiklarsan ham olcumler
 * acilir" diyor. Aciliyordu - ama backend'in sozluk anahtarlariyla:
 * `INLIER_COUNT`, `VISUAL_COVERAGE`, `ROTATION_DEG`. Projenin
 * aciklanabilirlik iddiasinin en dip katmani, ingilizce degisken
 * adlariyla yaziliydi. Ustelik karisik: `esik` ve `tam` Turkce,
 * `hamming` ve `cosine` ingilizce.
 *
 * Bicimlendirme `api.ts`'teki yardimcilarla; ondalik ayraci ve yuzde
 * kurali orada tanimli ve tek yerde kalmali.
 *
 * `birim` degeri sayidan sonra yazilir; `ipucu` `<dt>` uzerinde
 * baslik olarak durur ve olcumun ne oldugunu bir cumleyle anlatir.
 */
type Bicim = "oran" | "ondalik" | "tamsayi" | "evet-hayir" | "metin";

interface OlcumMeta {
  etiket: string;
  bicim: Bicim;
  birim?: string;
  ipucu?: string;
}

const OLCUM_META: Record<string, OlcumMeta> = {
  // Geometrik dogrulama
  good_matches: {
    etiket: "Aday eşleşme",
    bicim: "tamsayi",
    ipucu: "Oran testini geçen ham anahtar nokta çifti sayısı.",
  },
  inlier_count: {
    etiket: "Doğrulanan nokta",
    bicim: "tamsayi",
    ipucu: "RANSAC'ın tek bir dönüşümle açıklayabildiği eşleşme sayısı.",
  },
  inlier_ratio: {
    etiket: "Doğrulanan oran",
    bicim: "oran",
    ipucu: "Doğrulanan noktaların aday eşleşmelere oranı.",
  },
  geometric_coverage: {
    etiket: "Geometrik alan",
    bicim: "oran",
    ipucu: "Kaynağın türev üzerine düşürüldüğü dörtgenin kapladığı alan.",
  },
  visual_coverage: {
    etiket: "İçerikte kullanılan alan",
    bicim: "oran",
    ipucu: "Piksel doğrulamasından sonra kalan alan — pay hesabına giren sayı.",
  },
  source_usage: {
    etiket: "Kaynağın kullanılan bölümü",
    bicim: "oran",
    ipucu: "Kaynak görselin ne kadarı türevde kullanılmış.",
  },
  scale: {
    etiket: "Ölçek",
    bicim: "ondalik",
    birim: "×",
    ipucu: "Kaynak, türevde bu katsayıyla büyütülmüş/küçültülmüş.",
  },
  rotation_deg: { etiket: "Dönme", bicim: "ondalik", birim: "°" },
  mirrored: { etiket: "Aynalanmış", bicim: "evet-hayir" },
  reason: { etiket: "Gerekçe", bicim: "metin" },
  // Itiraz uzerine yeniden olcum (`services/ingest.remeasure`). Bu
  // anahtar ilk envanterde atlanmisti ve ekranda ham haliyle
  // "REMEASURED evet" diye gorundu - tanimsiz anahtarin gizlenmemesi
  // sayesinde fark edildi.
  remeasured: {
    etiket: "İtiraz üzerine yeniden ölçüldü",
    bicim: "evet-hayir",
    ipucu: "Bu ölçüm, itirazdan sonra daha hassas dedektörle (SIFT) tekrarlandı.",
  },

  // Goruntu parmak izi
  // Bulgu B5: "hash benzeri teknik ifade yadırgattı" (K5, Gorev 5).
  // Etiket artik matematiksel adi degil ne oldugunu soyluyor; teknik
  // terim (Hamming uzakligi) ipucunda duruyor.
  hamming: {
    etiket: "Fark biti sayısı",
    bicim: "tamsayi",
    birim: " bit",
    ipucu: "İki görüntü parmak izi arasında farklı olan bit sayısı (Hamming uzaklığı); küçük olması iyi.",
  },
  esik: {
    etiket: "Eşik",
    bicim: "tamsayi",
    birim: " bit",
    ipucu: "Bu değerin altındaki uzaklık eşleşme sayılır.",
  },
  region: {
    etiket: "Bölge",
    bicim: "metin",
    ipucu: "Sorgu görselinin hangi parçasından üretildiği.",
  },

  // Gorsel benzerlik
  cosine: {
    etiket: "Kosinüs benzerliği",
    bicim: "ondalik",
    ipucu: "CLIP gömme uzayında iki görselin yakınlığı; 1,00 aynı yöndür.",
  },

  // Icerik kimligi ve filigran
  manifest_urn: { etiket: "Manifest kimliği", bicim: "metin" },
  issuer: { etiket: "İmzalayan", bicim: "metin" },
  validation: { etiket: "İmza doğrulaması", bicim: "metin" },
  content_hash: {
    etiket: "Dosya özeti",
    bicim: "metin",
    ipucu: "SHA-256; birebir aynı dosyayı yakalar.",
  },
  tag: { etiket: "Filigran kimliği", bicim: "metin" },
  vote_confidence: {
    etiket: "Filigran oy güveni",
    bicim: "ondalik",
    ipucu: "Gömülü bitlerin çoğunluk oyunda ne kadar tutarlı çıktığı.",
  },
};

function bicimlendir(value: unknown, bicim: Bicim): string {
  if (value === null || value === undefined) return "—";
  switch (bicim) {
    case "oran":
      return typeof value === "number" ? pct(value) : String(value);
    case "ondalik":
      return typeof value === "number" ? sayi(value) : String(value);
    case "tamsayi":
      return typeof value === "number" ? String(Math.round(value)) : String(value);
    case "evet-hayir":
      return value ? "evet" : "hayır";
    default:
      return String(value);
  }
}

/**
 * Tanimsiz bir anahtar **gizlenmez**, ham haliyle gosterilir.
 *
 * Backend yeni bir olcum eklediginde ekrandan sessizce kaybolmasin.
 * Bu projede bir olcumu saklamak, cirkin gostermekten kotudur.
 */
function olcumSatiri(key: string, value: unknown): {
  etiket: string;
  deger: string;
  ipucu?: string;
} {
  const meta = OLCUM_META[key];
  if (!meta) return { etiket: key, deger: formatValue(value) };
  return {
    etiket: meta.etiket,
    deger: bicimlendir(value, meta.bicim) + (meta.birim ?? ""),
    ipucu: meta.ipucu,
  };
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "evet" : "hayır";
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : sayi(value, 4);
  }
  return String(value);
}
