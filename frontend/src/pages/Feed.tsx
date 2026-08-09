/**
 * Akis: platformdaki gonderiler.
 *
 * Her kart, icerigin koken durumunu bir rozetle tasir. Amac, atfin
 * ayri bir ekrana gomulmus bir "ozellik" degil, akisin dogal parcasi
 * oldugunu gostermek.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, money, type Content } from "../api";
import {
  Avatar,
  Badge,
  Button,
  CardSkeleton,
  ErrorNote,
  Field,
  Panel,
  inputClass,
} from "../components/ui";
import { useSession } from "../session";

export default function Feed() {
  const [items, setItems] = useState<Content[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  const load = useCallback(() => {
    api
      .feed()
      .then(setItems)
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(load, [load]);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Akış</h1>
          <p className="mt-1 text-[13px] text-[var(--color-ink-2)]">
            Her gönderinin kökeni yüklendiği anda çözülür; kaynak zincirini ve
            pay dağılımını gönderiye girerek görebilirsiniz.
          </p>
        </div>
        <Button
          variant={showUpload ? "default" : "primary"}
          onClick={() => setShowUpload((v) => !v)}
        >
          {showUpload ? "Kapat" : "İçerik yükle"}
        </Button>
      </div>

      {showUpload && (
        <UploadPanel
          onDone={() => {
            setShowUpload(false);
            load();
          }}
        />
      )}

      {error && <ErrorNote error={error} />}

      {items && items.length === 0 && (
        <Panel>
          <p className="py-8 text-center text-[13px] text-[var(--color-ink-2)]">
            Henüz gönderi yok. Demo verisini kurmak için{" "}
            <code className="num text-[12px] text-[var(--color-gold)]">
              python scripts/seed_demo.py --reset
            </code>{" "}
            komutunu çalıştırın.
          </p>
        </Panel>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {!items && !error && <CardSkeleton adet={3} />}
        {items?.map((item, i) => (
          // Kartlar sirayla beliriyor; hepsinin ayni anda patlamasi
          // yerine gozun akisi takip etmesini kolaylastiriyor.
          <ContentCard key={item.id} content={item} sira={i} />
        ))}
      </div>
    </div>
  );
}

function ContentCard({ content, sira = 0 }: { content: Content; sira?: number }) {
  return (
    <article
      className="fade-in panel group overflow-hidden transition-colors hover:border-[#3a4250]"
      style={{ animationDelay: `${Math.min(sira, 8) * 45}ms` }}
    >
      <Link to={`/icerik/${content.id}`} className="block">
        <div className="aspect-4/3 overflow-hidden bg-[var(--color-bg)]">
          <img
            src={api.imageUrl(content.id)}
            alt={content.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
          />
        </div>
      </Link>
      <div className="space-y-2.5 p-4">
        <div className="flex items-start justify-between gap-2">
          <Link
            to={`/icerik/${content.id}`}
            className="min-w-0 text-[14px] leading-snug font-semibold hover:text-[var(--color-gold)]"
          >
            {content.title}
          </Link>
          {content.revenue > 0 && (
            <span className="num shrink-0 text-[12.5px] font-semibold text-[var(--color-gold)]">
              {money(content.revenue)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Avatar
            name={content.owner.display_name}
            accent={content.owner.accent}
            size={22}
          />
          <span className="truncate text-[12.5px] text-[var(--color-ink-2)]">
            {content.owner.display_name}
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {content.source_count > 0 ? (
            <Badge tone="link">{content.source_count} kaynak</Badge>
          ) : (
            <Badge tone="verify">özgün</Badge>
          )}
          {content.derivative_count > 0 && (
            <Badge tone="neutral">{content.derivative_count} türev</Badge>
          )}
          {!content.remix_allowed && <Badge tone="alert">remix kapalı</Badge>}
        </div>

        <div className="flex gap-2 pt-0.5">
          <Link to={`/icerik/${content.id}`} className="flex-1">
            <Button className="w-full">Emek Kartı</Button>
          </Link>
          {content.remix_allowed && (
            <Link to={`/remix/${content.id}`}>
              <Button variant="ghost">Remixle</Button>
            </Link>
          )}
        </div>
      </div>
    </article>
  );
}

/* -------------------------------------------------------------------------- */
function UploadPanel({ onDone }: { onDone: () => void }) {
  const { currentUser } = useSession();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [caption, setCaption] = useState("");
  const [minShare, setMinShare] = useState(0);
  const [remixAllowed, setRemixAllowed] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function submit() {
    if (!file || !currentUser) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("owner_id", currentUser.id);
      form.append("title", title || file.name);
      form.append("caption", caption);
      form.append("remix_allowed", String(remixAllowed));
      form.append("min_source_share", String(minShare / 100));
      const res = await api.upload(form);
      setResult(
        res.recovery.links.length > 0
          ? `Yayınlandı. Köken hattı ${res.recovery.links.length} kaynak buldu — içeriğe girip Emek Kartı'na bakın.`
          : "Yayınlandı. Kaynak bulunamadı; içerik özgün kabul edildi ve imzalandı.",
      );
      setTimeout(onDone, 1600);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Panel
      title="İçerik yükle"
      subtitle="Yükleme anında köken kurtarma hattı çalışır: içerik kimliği okunur, yoksa kanıtlardan zincir kurulmaya çalışılır."
    >
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <Field label="Görsel">
            {/* Buton, div degil: gizli dosya alani sekme sirasinda
                olmadigi icin tiklanabilir bir div klavyeyle acilamiyordu. */}
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const dropped = e.dataTransfer.files?.[0];
                if (dropped) setFile(dropped);
              }}
              aria-label={file ? `Seçilen dosya: ${file.name}. Değiştir` : "Yüklenecek görseli seç"}
              className="flex w-full cursor-pointer items-center justify-center rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-bg)] px-4 py-6 text-center text-[13px] text-[var(--color-ink-3)] hover:border-[var(--color-link)]"
            >
              {file ? (
                <span className="text-[var(--color-ink)]">{file.name}</span>
              ) : (
                "Sürükleyin ya da seçmek için tıklayın"
              )}
            </button>
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </Field>
          <Field label="Başlık">
            <input
              className={inputClass}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Sabah ışığı"
            />
          </Field>
          <Field label="Açıklama">
            <input
              className={inputClass}
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Kendi çektiğim kare."
            />
          </Field>
        </div>

        <div className="space-y-3">
          <Field
            label="Remix izni"
            hint="Kapatırsanız içeriğiniz remix stüdyosunda açılamaz."
          >
            <label className="flex items-center gap-2 text-[13px]">
              <input
                type="checkbox"
                checked={remixAllowed}
                onChange={(e) => setRemixAllowed(e.target.checked)}
                className="h-4 w-4 accent-[var(--color-gold)]"
              />
              Bu içerik remixlenebilir
            </label>
          </Field>

          <Field
            label={`Asgari kaynak payı talebi: %${minShare}`}
            hint="Bu tercih içerik kimliğine yazılır ve içerikle birlikte seyahat eder. Üretici tabanını aşamaz."
          >
            <input
              type="range"
              min={0}
              max={50}
              step={5}
              value={minShare}
              onChange={(e) => setMinShare(Number(e.target.value))}
              className="w-full accent-[var(--color-gold)]"
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
            onClick={submit}
            disabled={!file || busy}
            className="w-full"
          >
            {busy ? "Köken çözülüyor…" : "Yayınla"}
          </Button>
        </div>
      </div>
    </Panel>
  );
}
