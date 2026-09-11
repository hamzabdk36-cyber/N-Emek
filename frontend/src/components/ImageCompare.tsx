/**
 * Kaynak ve turev gorseli yan yana; turevin uzerinde "bu bolge
 * kaynaktan geliyor" maskesi.
 *
 * Maske, backend'in geometri asamasinda urettigi PNG'dir (beyaz =
 * korunmus piksel). CSS `mask-image` yerine canvas uzerinde
 * birlestiriyoruz: `mask-mode: luminance` tarayici destegi tutarsiz ve
 * bu ekran demonun en kritik goruntusu - calismama riski alinmaz.
 */
import { useEffect, useRef, useState } from "react";
import { pct } from "../api";

export function ImageCompare({
  sourceUrl,
  derivativeUrl,
  maskUrl,
  sourceLabel,
  derivativeLabel,
  coverage,
}: {
  sourceUrl: string;
  derivativeUrl: string;
  maskUrl?: string | null;
  sourceLabel: string;
  derivativeLabel: string;
  coverage?: number | null;
}) {
  const [showMask, setShowMask] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!maskUrl) return;
    let cancelled = false;
    setReady(false);
    setFailed(false);

    const load = (url: string) =>
      new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error(url));
        img.src = url;
      });

    Promise.all([load(derivativeUrl), load(maskUrl)])
      .then(([base, mask]) => {
        if (cancelled) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = base.naturalWidth;
        canvas.height = base.naturalHeight;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        ctx.drawImage(base, 0, 0);

        // Maskeyi turev cozunurlugune olcekleyip oku.
        const scratch = document.createElement("canvas");
        scratch.width = canvas.width;
        scratch.height = canvas.height;
        const sctx = scratch.getContext("2d");
        if (!sctx) return;
        sctx.drawImage(mask, 0, 0, canvas.width, canvas.height);

        const maskData = sctx.getImageData(0, 0, canvas.width, canvas.height);
        const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const px = frame.data;
        const mk = maskData.data;
        // Ayrimi *kontrastla* kuruyoruz, renkle degil: eslesen bolge
        // hafif yesile calarak parlak kalir, eslesmeyen bolge griye
        // duser ve karartilir. Yogun bir yesil katman, kapsamanin %90'i
        // astigi tipik durumda goruntuyu tamamen yutuyordu.
        for (let i = 0; i < px.length; i += 4) {
          if (mk[i] > 127) {
            px[i] = px[i] * 0.88;
            px[i + 1] = px[i + 1] * 0.88 + 0.12 * 210;
            px[i + 2] = px[i + 2] * 0.88 + 0.12 * 150;
          } else {
            const gray = 0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2];
            px[i] = gray * 0.42;
            px[i + 1] = gray * 0.42;
            px[i + 2] = gray * 0.44;
          }
        }
        ctx.putImageData(frame, 0, 0);
        setReady(true);
      })
      .catch(() => !cancelled && setFailed(true));

    return () => {
      cancelled = true;
    };
  }, [derivativeUrl, maskUrl]);

  const hasMask = Boolean(maskUrl) && !failed;

  return (
    <div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Figure label={sourceLabel} caption="kaynak içerik">
          <img
            src={sourceUrl}
            alt={sourceLabel}
            className="block h-full w-full object-cover"
            loading="lazy"
          />
        </Figure>

        <Figure
          label={derivativeLabel}
          caption={
            hasMask && showMask
              ? `parlak alan: ${sourceLabel}'dan geldiği ölçümle doğrulanan bölge`
              : "türev içerik"
          }
        >
          <img
            src={derivativeUrl}
            alt={derivativeLabel}
            className={`block h-full w-full object-cover ${
              hasMask && showMask && ready ? "invisible absolute" : ""
            }`}
            loading="lazy"
          />
          {hasMask && (
            <canvas
              ref={canvasRef}
              className={`block h-full w-full object-cover ${
                showMask && ready ? "" : "hidden"
              }`}
              aria-label="Eşleşen bölge vurgulanmış türev görsel"
            />
          )}
        </Figure>
      </div>

      {hasMask && (
        <div className="mt-3 space-y-2.5">
          {/* Bulgu B3: iki katilimci parlak alani "degistirilen bolge"
              sandi, halbuki tam tersi - kaynaktan geldigi olculen bolge.
              Renkle degil kontrastla kuruyoruz (CLAUDE.md renk
              disiplini); gosterge de ayni iki ornegi aciktan yaziyor,
              kaynagin adini da soyleyerek soyut "kaynak" kelimesinden
              kacinir. */}
          {showMask && (
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[11.5px] text-[var(--color-ink-3)]">
              <span className="flex items-center gap-1.5">
                <span
                  aria-hidden
                  className="h-3 w-3 rounded-sm border border-[var(--color-verify)]/50 bg-[var(--color-verify-dim)]"
                />
                parlak: {sourceLabel}'dan gelen piksel
              </span>
              <span className="flex items-center gap-1.5">
                <span
                  aria-hidden
                  className="h-3 w-3 rounded-sm border border-[var(--color-line)] bg-[var(--color-surface-2)]"
                />
                gri: {derivativeLabel} üreticisinin eklediği
              </span>
            </div>
          )}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <label className="flex cursor-pointer items-center gap-2 text-[12px] text-[var(--color-ink-2)]">
              <input
                type="checkbox"
                checked={showMask}
                onChange={(e) => setShowMask(e.target.checked)}
                className="h-3.5 w-3.5 accent-[var(--color-verify)]"
              />
              Kaynaktan gelen bölgeyi vurgula
            </label>
            {coverage != null && (
              <span className="num text-[12px] text-[var(--color-ink-2)]">
                ölçülen kullanılan alan:{" "}
                <span className="font-semibold text-[var(--color-verify)]">
                  {pct(coverage)}
                </span>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Figure({
  label,
  caption,
  children,
}: {
  label: string;
  caption: string;
  children: React.ReactNode;
}) {
  return (
    <figure className="min-w-0">
      <div className="relative aspect-4/3 overflow-hidden rounded-lg border border-[var(--color-line)] bg-[var(--color-bg)]">
        {children}
      </div>
      <figcaption className="mt-2">
        <div className="truncate text-[13px] font-medium text-[var(--color-ink)]">
          {label}
        </div>
        <div className="text-[11.5px] text-[var(--color-ink-3)]">{caption}</div>
      </figcaption>
    </figure>
  );
}
