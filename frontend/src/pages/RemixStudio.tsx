/**
 * Remix Studyosu.
 *
 * Canvas uzerinde dort islem: kirpma, yazi, cizim, filtre. Her islem
 * ayni zamanda bir C2PA eylemine (`c2pa.cropped`, `c2pa.drawing`,
 * `c2pa.color_adjustments`) karsilik gelir ve yayinlanan manifeste
 * yazilir - yani duzenleme gecmisi kayit altina alinir.
 *
 * Onemli tasarim notu: studyo kaynagi *beyan eder* ama pay hesabi
 * beyana degil olcume dayanir. Kullanici "bunu kullandim" dese bile
 * sistem ne kadarini kullandigini kendisi olcer.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type Content } from "../api";
import {
  Badge,
  Button,
  ErrorNote,
  Field,
  Panel,
  Spinner,
  inputClass,
} from "../components/ui";
import { useSession } from "../session";

type Tool = "kirp" | "yazi" | "cizim" | "yok";
type FilterName = "yok" | "sicak" | "soguk" | "mono" | "canli";

const FILTERS: Record<FilterName, { label: string; css: string }> = {
  yok: { label: "Filtresiz", css: "none" },
  sicak: { label: "Sıcak", css: "sepia(0.35) saturate(1.3) brightness(1.05)" },
  soguk: { label: "Soğuk", css: "hue-rotate(-18deg) saturate(1.15) contrast(1.08)" },
  mono: { label: "Siyah-beyaz", css: "grayscale(1) contrast(1.12)" },
  canli: { label: "Canlı", css: "saturate(1.65) contrast(1.15)" },
};

interface TextLayer {
  x: number;
  y: number;
  text: string;
  size: number;
  color: string;
}
interface Stroke {
  points: { x: number; y: number }[];
  color: string;
  width: number;
}
interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export default function RemixStudio() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useSession();

  const [source, setSource] = useState<Content | null>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [tool, setTool] = useState<Tool>("yok");
  const [crop, setCrop] = useState<Rect | null>(null);
  const [pendingCrop, setPendingCrop] = useState<Rect | null>(null);
  const [texts, setTexts] = useState<TextLayer[]>([]);
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [filter, setFilter] = useState<FilterName>("yok");

  const [textDraft, setTextDraft] = useState("SEHRIN RENKLERI");
  const [inkColor, setInkColor] = useState("#f2b134");
  const [brush, setBrush] = useState(8);

  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef<Stroke | null>(null);
  const dragStart = useRef<{ x: number; y: number } | null>(null);

  /* -- kaynagi yukle ---------------------------------------------------- */
  useEffect(() => {
    api
      .content(id)
      .then((c) => {
        setSource(c);
        setTitle(`${c.title} — remix`);
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => setImage(img);
        img.onerror = () => setError("Kaynak görsel yüklenemedi.");
        img.src = api.imageUrl(id);
      })
      .catch((e: Error) => setError(e.message));
  }, [id]);

  /* -- cizim ------------------------------------------------------------- */
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !image) return;
    const area: Rect = crop ?? {
      x: 0,
      y: 0,
      w: image.naturalWidth,
      h: image.naturalHeight,
    };
    canvas.width = area.w;
    canvas.height = area.h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.filter = FILTERS[filter].css;
    ctx.drawImage(image, area.x, area.y, area.w, area.h, 0, 0, area.w, area.h);
    ctx.filter = "none";

    for (const stroke of strokes) {
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.width;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      stroke.points.forEach((p, i) => {
        const x = p.x - area.x;
        const y = p.y - area.y;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    for (const layer of texts) {
      ctx.font = `700 ${layer.size}px Inter, system-ui, sans-serif`;
      ctx.textBaseline = "middle";
      const x = layer.x - area.x;
      const y = layer.y - area.y;
      const metrics = ctx.measureText(layer.text);
      // Okunurluk icin arkaya koyu bir serit: yazi her zeminde okunsun.
      ctx.fillStyle = "rgba(10,12,15,0.72)";
      ctx.fillRect(
        x - 12,
        y - layer.size * 0.72,
        metrics.width + 24,
        layer.size * 1.44,
      );
      ctx.fillStyle = layer.color;
      ctx.fillText(layer.text, x, y);
    }

    if (pendingCrop) {
      ctx.strokeStyle = "#f2b134";
      ctx.lineWidth = Math.max(2, area.w / 400);
      ctx.setLineDash([10, 8]);
      ctx.strokeRect(
        pendingCrop.x - area.x,
        pendingCrop.y - area.y,
        pendingCrop.w,
        pendingCrop.h,
      );
      ctx.setLineDash([]);
    }
  }, [image, crop, filter, strokes, texts, pendingCrop]);

  useEffect(render, [render]);

  /* -- fare olaylari ----------------------------------------------------- */
  function toImageCoords(e: React.MouseEvent<HTMLCanvasElement>) {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const area: Rect = crop ?? {
      x: 0,
      y: 0,
      w: image!.naturalWidth,
      h: image!.naturalHeight,
    };
    return {
      x: area.x + ((e.clientX - rect.left) / rect.width) * area.w,
      y: area.y + ((e.clientY - rect.top) / rect.height) * area.h,
    };
  }

  function onDown(e: React.MouseEvent<HTMLCanvasElement>) {
    if (!image) return;
    const p = toImageCoords(e);
    if (tool === "cizim") {
      drawing.current = { points: [p], color: inkColor, width: brush };
      setStrokes((prev) => [...prev, drawing.current!]);
    } else if (tool === "kirp") {
      dragStart.current = p;
    } else if (tool === "yazi" && textDraft.trim()) {
      const area = crop ?? { w: image.naturalWidth };
      setTexts((prev) => [
        ...prev,
        {
          x: p.x,
          y: p.y,
          text: textDraft,
          size: Math.round(area.w / 14),
          color: inkColor,
        },
      ]);
    }
  }

  function onMove(e: React.MouseEvent<HTMLCanvasElement>) {
    if (!image) return;
    const p = toImageCoords(e);
    if (drawing.current) {
      // Aktif cizgi zaten listede; son ogeyi yeni noktayla degistirerek
      // yeniden cizimi tetikliyoruz.
      const updated: Stroke = {
        ...drawing.current,
        points: [...drawing.current.points, p],
      };
      drawing.current = updated;
      setStrokes((prev) => [...prev.slice(0, -1), updated]);
    } else if (dragStart.current) {
      const s = dragStart.current;
      setPendingCrop({
        x: Math.min(s.x, p.x),
        y: Math.min(s.y, p.y),
        w: Math.abs(p.x - s.x),
        h: Math.abs(p.y - s.y),
      });
    }
  }

  function onUp() {
    drawing.current = null;
    dragStart.current = null;
  }

  function applyCrop() {
    if (!pendingCrop || pendingCrop.w < 32 || pendingCrop.h < 32) return;
    setCrop({
      x: Math.round(pendingCrop.x),
      y: Math.round(pendingCrop.y),
      w: Math.round(pendingCrop.w),
      h: Math.round(pendingCrop.h),
    });
    setPendingCrop(null);
    setTool("yok");
  }

  function reset() {
    setCrop(null);
    setPendingCrop(null);
    setTexts([]);
    setStrokes([]);
    setFilter("yok");
  }

  /* -- yayinla ----------------------------------------------------------- */
  const actions: string[] = [];
  if (crop) actions.push("c2pa.cropped");
  if (strokes.length) actions.push("c2pa.drawing");
  if (texts.length) actions.push("c2pa.edited");
  if (filter !== "yok") actions.push("c2pa.color_adjustments");

  async function publish() {
    const canvas = canvasRef.current;
    if (!canvas || !currentUser) return;
    setBusy(true);
    setError(null);
    try {
      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", 0.92),
      );
      if (!blob) throw new Error("Görsel dışa aktarılamadı.");
      const form = new FormData();
      form.append("file", blob, "remix.jpg");
      form.append("owner_id", currentUser.id);
      form.append("title", title || "Remix");
      form.append("actions", actions.join(",") || "c2pa.edited");
      const res = await api.remix(id, form);
      const link = res.recovery.links[0];
      setResult(
        link?.visual_coverage != null
          ? `Yayınlandı. Ölçüm: içeriğin %${(link.visual_coverage * 100).toFixed(1)}'i kaynaktan geliyor.`
          : "Yayınlandı.",
      );
      setTimeout(() => navigate(`/icerik/${res.content.id}`), 1400);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (error && !source) return <ErrorNote error={error} />;
  if (!source || !image) return <Spinner label="Stüdyo hazırlanıyor…" />;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Remix Stüdyosu</h1>
        <p className="mt-1 text-[13px] text-[var(--color-ink-2)]">
          Kaynak: <span className="text-[var(--color-ink)]">{source.title}</span>{" "}
          · {source.owner.display_name}. Yaptığınız her işlem içerik kimliğine
          yazılır; pay ise beyana değil, ölçüme göre hesaplanır.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_300px]">
        <Panel
          title="Tuval"
          right={
            <div className="flex flex-wrap gap-1.5">
              {actions.map((a) => (
                <Badge key={a} tone="link">
                  {a.replace("c2pa.", "")}
                </Badge>
              ))}
            </div>
          }
        >
          <canvas
            ref={canvasRef}
            onMouseDown={onDown}
            onMouseMove={onMove}
            onMouseUp={onUp}
            onMouseLeave={onUp}
            role="img"
            aria-label={
              `Remix tuvali. Kaynak: ${source.title}. ` +
              `${crop ? "Kırpılmış. " : ""}` +
              `${texts.length} yazı katmanı, ${strokes.length} çizim, ` +
              `filtre: ${filter === "yok" ? "uygulanmadı" : filter}.`
            }
            className="w-full rounded-lg border border-[var(--color-line)]"
            style={{
              cursor:
                tool === "cizim"
                  ? "crosshair"
                  : tool === "kirp"
                    ? "crosshair"
                    : tool === "yazi"
                      ? "text"
                      : "default",
            }}
          />
          {pendingCrop && (
            <div className="mt-3 flex items-center gap-2">
              <Button variant="primary" onClick={applyCrop}>
                Kırpmayı uygula
              </Button>
              <Button variant="ghost" onClick={() => setPendingCrop(null)}>
                Vazgeç
              </Button>
              <span className="num text-[12px] text-[var(--color-ink-3)]">
                {Math.round(pendingCrop.w)}×{Math.round(pendingCrop.h)}
              </span>
            </div>
          )}
        </Panel>

        <div className="space-y-5">
          <Panel title="Araçlar">
            <div className="grid grid-cols-2 gap-2">
              <ToolButton active={tool === "kirp"} onClick={() => setTool("kirp")}>
                Kırp
              </ToolButton>
              <ToolButton active={tool === "yazi"} onClick={() => setTool("yazi")}>
                Yazı
              </ToolButton>
              <ToolButton active={tool === "cizim"} onClick={() => setTool("cizim")}>
                Çizim
              </ToolButton>
              <ToolButton active={tool === "yok"} onClick={() => setTool("yok")}>
                Seçimi bırak
              </ToolButton>
            </div>

            {tool === "kirp" && (
              <KeyboardCrop
                image={image}
                crop={crop}
                pendingCrop={pendingCrop}
                onChange={setPendingCrop}
              />
            )}

            <div className="mt-4 space-y-3">
              <Field label="Yazı metni" hint="Tuvale tıklayarak yerleştirin.">
                <input
                  className={inputClass}
                  value={textDraft}
                  onChange={(e) => setTextDraft(e.target.value)}
                />
              </Field>

              <div className="grid grid-cols-2 gap-3">
                <Field label="Renk">
                  <input
                    type="color"
                    value={inkColor}
                    onChange={(e) => setInkColor(e.target.value)}
                    className="h-9 w-full cursor-pointer rounded-lg border border-[var(--color-line)] bg-[var(--color-bg)]"
                  />
                </Field>
                <Field label={`Fırça ${brush}px`}>
                  <input
                    type="range"
                    min={2}
                    max={40}
                    value={brush}
                    onChange={(e) => setBrush(Number(e.target.value))}
                    className="w-full accent-[var(--color-gold)]"
                  />
                </Field>
              </div>

              <Field label="Filtre">
                <div className="grid grid-cols-2 gap-1.5">
                  {(Object.keys(FILTERS) as FilterName[]).map((name) => (
                    <ToolButton
                      key={name}
                      active={filter === name}
                      onClick={() => setFilter(name)}
                    >
                      {FILTERS[name].label}
                    </ToolButton>
                  ))}
                </div>
              </Field>

              <Button variant="ghost" onClick={reset} className="w-full">
                Tümünü sıfırla
              </Button>
            </div>
          </Panel>

          <Panel title="Yayınla">
            <div className="space-y-3">
              <Field label="Başlık">
                <input
                  className={inputClass}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </Field>
              {error && <ErrorNote error={error} />}
              {result && (
                <div className="rounded-lg border border-[var(--color-verify)]/40 bg-[var(--color-verify-dim)]/40 px-3.5 py-2.5 text-[12.5px] text-[var(--color-verify)]">
                  {result}
                </div>
              )}
              <Button
                variant="primary"
                onClick={publish}
                disabled={busy}
                className="w-full"
              >
                {busy ? "Ölçülüyor ve imzalanıyor…" : "Remixi yayınla"}
              </Button>
              <p className="text-[11.5px] leading-relaxed text-[var(--color-ink-3)]">
                Yayınlarken kaynak bağı kurulur, kullanılan alan oranı ölçülür
                ve C2PA manifesti eylem listesiyle birlikte imzalanır.
              </p>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}

function ToolButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`rounded-lg border px-3 py-2 text-[12.5px] font-medium transition-colors ${
        active
          ? "border-[var(--color-gold)]/50 bg-[var(--color-gold-dim)]/40 text-[var(--color-gold)]"
          : "border-[var(--color-line)] bg-[var(--color-surface-2)] text-[var(--color-ink-2)] hover:text-[var(--color-ink)]"
      }`}
    >
      {children}
    </button>
  );
}

/**
 * Kirpmanin klavyeyle yapilabilen karsiligi.
 *
 * Tuval uzerinde surukleyerek kirpmak fareye bagli. WCAG 2.1.1,
 * kullanicinin *hareket yoluna* bagli girdileri (serbest el cizim gibi)
 * bu kuraldan muaf tutuyor - ama kirpma oyle degil: bir dikdortgen,
 * dort sayiyla ifade edilebilir. Bu yuzden kirpma araci secildiginde
 * sayisal alanlar da aciliyor ve klavyeyle gezen kullanici ayni isi
 * yapabiliyor.
 */
function KeyboardCrop({
  image,
  crop,
  pendingCrop,
  onChange,
}: {
  image: HTMLImageElement | null;
  crop: Rect | null;
  pendingCrop: Rect | null;
  onChange: (rect: Rect | null) => void;
}) {
  if (!image) return null;
  const area: Rect = crop ?? {
    x: 0,
    y: 0,
    w: image.naturalWidth,
    h: image.naturalHeight,
  };
  const rect = pendingCrop ?? area;

  const set = (key: keyof Rect, value: number) => {
    const next = { ...rect, [key]: Math.max(0, Math.round(value)) };
    // Secim kaynak alaninin disina tasmasin.
    next.w = Math.min(next.w, area.x + area.w - next.x);
    next.h = Math.min(next.h, area.y + area.h - next.y);
    onChange(next);
  };

  const alanlar: { key: keyof Rect; label: string; max: number }[] = [
    { key: "x", label: "Sol", max: area.x + area.w - 32 },
    { key: "y", label: "Üst", max: area.y + area.h - 32 },
    { key: "w", label: "Genişlik", max: area.w },
    { key: "h", label: "Yükseklik", max: area.h },
  ];

  return (
    <fieldset className="mt-4 rounded-lg border border-[var(--color-line)] px-3 py-2.5">
      <legend className="px-1 text-[11px] font-medium tracking-wide text-[var(--color-ink-3)] uppercase">
        Sayısal kırpma
      </legend>
      <p className="mb-2 text-[11.5px] leading-relaxed text-[var(--color-ink-3)]">
        Tuvalde sürükleyebilir ya da değerleri buradan girebilirsiniz. Piksel
        cinsinden.
      </p>
      <div className="grid grid-cols-2 gap-2">
        {alanlar.map((a) => (
          <Field key={a.key} label={a.label}>
            <input
              type="number"
              inputMode="numeric"
              min={a.key === "w" || a.key === "h" ? 32 : 0}
              max={Math.round(a.max)}
              value={Math.round(rect[a.key])}
              onChange={(e) => set(a.key, Number(e.target.value))}
              className={inputClass}
            />
          </Field>
        ))}
      </div>
    </fieldset>
  );
}
