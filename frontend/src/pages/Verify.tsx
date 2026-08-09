/**
 * Kaynak bul: bir gorseli yayinlamadan sorgulama.
 *
 * "Bu icerik kimden geliyor?" sorusunun tek adimlik cevabi. Ekranin
 * asil isi hattin *nasil* karar verdigini gostermek - hangi asama neyi
 * buldu, ne kadar surdu, hangi kanitla.
 */
import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, pctRaw, type RecoveryResult } from "../api";
import { EvidenceList, StageTimeline } from "../components/Pipeline";
import {
  Badge,
  Button,
  ConfidenceBadge,
  ErrorNote,
  Panel,
  Spinner,
} from "../components/ui";

export default function Verify() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<RecoveryResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function pick(next: File | null) {
    setFile(next);
    setResult(null);
    setError(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(next ? URL.createObjectURL(next) : null);
  }

  async function run() {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      setResult(await api.verify(form));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Kaynak bul</h1>
        <p className="mt-1 max-w-2xl text-[13px] leading-relaxed text-[var(--color-ink-2)]">
          Bir görselin kökenini platforma kaydetmeden sorgulayın. Hat sırasıyla
          içerik kimliğini, dosya özetini, gömülü filigranı, algısal parmak izini
          ve görsel benzerliği dener; bulduğu adayları geometrik olarak doğrular.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,380px)_minmax(0,1fr)]">
        <Panel title="Sorgulanacak görsel">
          {/* Buton, div degil: dosya alani `hidden` oldugu icin sekme
              sirasinda yok ve tiklanabilir bir div klavyeyle acilamiyordu -
              yani klavyeyle gezen kullanici hic gorsel yukleyemiyordu. */}
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              pick(e.dataTransfer.files?.[0] ?? null);
            }}
            aria-label={
              preview
                ? "Sorgulanacak görseli değiştir"
                : "Sorgulanacak görseli seç"
            }
            className="block w-full cursor-pointer overflow-hidden rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-bg)] hover:border-[var(--color-link)]"
          >
            {preview ? (
              <img src={preview} alt="Sorgulanacak görsel" className="w-full" />
            ) : (
              <span className="block px-4 py-14 text-center text-[13px] text-[var(--color-ink-3)]">
                Görseli sürükleyin ya da seçmek için tıklayın
              </span>
            )}
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => pick(e.target.files?.[0] ?? null)}
          />
          <Button
            variant="primary"
            onClick={run}
            disabled={!file || busy}
            className="mt-3 w-full"
          >
            {busy ? "Hat çalışıyor…" : "Kökeni çöz"}
          </Button>
          {error && (
            <div className="mt-3">
              <ErrorNote error={error} />
            </div>
          )}
        </Panel>

        <div className="space-y-5">
          {busy && (
            <Panel>
              <Spinner label="Beş aşama sırayla çalışıyor…" />
            </Panel>
          )}

          {result && (
            <>
              <Panel
                title="Köken kurtarma hattı"
                right={
                  result.manifest_present ? (
                    <Badge tone="verify">içerik kimliği var</Badge>
                  ) : (
                    <Badge tone="caution">içerik kimliği yok</Badge>
                  )
                }
              >
                <StageTimeline
                  stages={result.stage_log}
                  timings={result.timings_ms}
                />
              </Panel>

              <Panel
                title={`Bulunan kaynaklar (${result.links.length})`}
                subtitle="Sistem sahiplik kararı vermez; kanıtlarıyla birlikte bir zincir önerisi sunar."
              >
                {result.links.length === 0 ? (
                  <p className="py-6 text-center text-[13px] text-[var(--color-ink-2)]">
                    Kaynak bulunamadı. Görsel platformda kayıtlı hiçbir içerikle
                    ölçülebilir bir ilişki göstermiyor.
                  </p>
                ) : (
                  <ul className="space-y-3">
                    {result.links.map((link) => (
                      <li
                        key={link.parent_content_id}
                        className="rounded-lg border border-[var(--color-line-soft)] bg-[var(--color-surface-2)]/50 p-3.5"
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div className="flex min-w-0 items-start gap-3">
                            <img
                              src={api.imageUrl(link.parent_content_id)}
                              alt=""
                              className="h-14 w-14 shrink-0 rounded-md border border-[var(--color-line)] object-cover"
                            />
                            <div className="min-w-0">
                              <Link
                                to={`/icerik/${link.parent_content_id}`}
                                className="block truncate text-[13.5px] font-medium hover:text-[var(--color-gold)]"
                              >
                                {link.parent_title || link.parent_content_id}
                              </Link>
                              <div className="mt-1 flex flex-wrap items-center gap-1.5">
                                <ConfidenceBadge
                                  band={{
                                    level: link.confidence_level as
                                      | "yuksek"
                                      | "orta"
                                      | "dusuk",
                                    score: link.confidence,
                                    note: "",
                                  }}
                                />
                                <Badge tone="link">{link.stage_label}</Badge>
                                {link.geometry_verified ? (
                                  <Badge tone="verify">geometrik doğrulandı</Badge>
                                ) : (
                                  <Badge tone="caution">alan ölçülemedi</Badge>
                                )}
                              </div>
                            </div>
                          </div>
                          {link.visual_coverage != null && (
                            <div className="text-right">
                              <div className="num text-lg font-semibold text-[var(--color-verify)]">
                                {pctRaw(link.visual_coverage * 100)}
                              </div>
                              <div className="text-[10.5px] tracking-wide text-[var(--color-ink-3)] uppercase">
                                kullanılan alan
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="mt-3">
                          <EvidenceList rows={link.evidence} />
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </Panel>
            </>
          )}

          {!result && !busy && (
            <Panel>
              <p className="py-10 text-center text-[13px] text-[var(--color-ink-3)]">
                Sonuçlar burada görünecek.
              </p>
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
