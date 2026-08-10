/**
 * Insan inceleme kuyrugu.
 *
 * Sistemin "makine her seyi cozer" iddiasi yok. Yeniden olcum de sonuc
 * vermediginde itiraz buraya duser ve karari bir insan verir. Bu ekran,
 * o siniri gizlemek yerine urunun parcasi haline getiriyor.
 */
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, pctRaw, sayi, type DisputeQueueItem } from "../api";
import {
  Badge,
  Button,
  ErrorNote,
  Field,
  Panel,
  Spinner,
  inputClass,
} from "../components/ui";

const STATUS_LABEL: Record<string, { label: string; tone: "caution" | "alert" }> = {
  open: { label: "yeni itiraz", tone: "caution" },
  escalated: { label: "makine karar veremedi", tone: "alert" },
};

export default function Moderation() {
  const [items, setItems] = useState<DisputeQueueItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    api
      .disputeQueue()
      .then(setItems)
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(load, [load]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">İnceleme kuyruğu</h1>
        <p className="mt-1 max-w-2xl text-[13px] leading-relaxed text-[var(--color-ink-2)]">
          İtirazlar önce otomatik değerlendirilir: bağ, daha hassas bir
          dedektörle yeniden ölçülür. Ölçüm yine sonuç vermezse karar insana
          bırakılır — sistem karar veremediği yeri gizlemez.
        </p>
      </div>

      {error && <ErrorNote error={error} />}
      {!items && !error && <Spinner label="Kuyruk yükleniyor…" />}

      {items && items.length === 0 && (
        <Panel>
          <p className="py-10 text-center text-[13px] text-[var(--color-ink-2)]">
            Kuyruk boş. Bekleyen veya insana yükseltilmiş itiraz yok.
          </p>
        </Panel>
      )}

      <div className="space-y-4">
        {items?.map((item) => (
          <DisputeCard key={item.id} item={item} onDone={load} />
        ))}
      </div>
    </div>
  );
}

function DisputeCard({
  item,
  onDone,
}: {
  item: DisputeQueueItem;
  onDone: () => void;
}) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const status = STATUS_LABEL[item.status] ?? {
    label: item.status,
    tone: "caution" as const,
  };
  const resolution = item.resolution as {
    summary?: string;
    before?: { confidence?: number; visual_coverage?: number | null };
    after?: { confidence?: number; visual_coverage?: number | null };
  };

  async function decide(accept: boolean) {
    setBusy(true);
    setError(null);
    try {
      await api.moderate(item.id, accept, note);
      onDone();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Panel
      title={`İtiraz · ${item.raiser}`}
      subtitle={new Date(item.created_at).toLocaleString("tr-TR")}
      right={<Badge tone={status.tone}>{status.label}</Badge>}
    >
      <p className="text-[13px] leading-relaxed text-[var(--color-ink)]">
        {item.reason}
      </p>

      {item.edge.parent_id && item.edge.child_id && (
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <EdgeSide
            label="İtiraz edilen kaynak"
            contentId={item.edge.parent_id}
          />
          <EdgeSide label="Türev içerik" contentId={item.edge.child_id} />
        </div>
      )}

      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Measure
          label="Güven (önce)"
          value={
            resolution.before?.confidence != null
              ? sayi(resolution.before.confidence)
              : "—"
          }
        />
        <Measure
          label="Güven (sonra)"
          value={
            resolution.after?.confidence != null
              ? sayi(resolution.after.confidence)
              : "—"
          }
        />
        <Measure
          label="Alan (önce)"
          value={
            resolution.before?.visual_coverage != null
              ? pctRaw(resolution.before.visual_coverage * 100)
              : "ölçülemedi"
          }
        />
        <Measure
          label="Alan (sonra)"
          value={
            resolution.after?.visual_coverage != null
              ? pctRaw(resolution.after.visual_coverage * 100)
              : "ölçülemedi"
          }
        />
      </div>

      {resolution.summary && (
        <p className="mt-3 rounded-lg border border-[var(--color-line-soft)] bg-[var(--color-surface-2)]/50 px-3.5 py-2.5 text-[12.5px] leading-relaxed text-[var(--color-ink-2)]">
          {resolution.summary}
        </p>
      )}

      <div className="mt-4 space-y-3 border-t border-[var(--color-line-soft)] pt-4">
        <Field
          label="Moderatör notu"
          hint="Karar ve gerekçe kayda geçer; taraflar görebilir."
        >
          <textarea
            className={`${inputClass} min-h-16 resize-y`}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="İtiraz sahibinin sunduğu orijinal dosya, iddiayı doğruluyor."
          />
        </Field>
        {error && <ErrorNote error={error} />}
        <div className="flex flex-wrap gap-2">
          <Button variant="primary" onClick={() => decide(true)} disabled={busy}>
            İtirazı kabul et ve bağı kaldır
          </Button>
          <Button onClick={() => decide(false)} disabled={busy}>
            İtirazı reddet, bağı onayla
          </Button>
        </div>
      </div>
    </Panel>
  );
}

function EdgeSide({ label, contentId }: { label: string; contentId: string }) {
  return (
    <div>
      <div className="mb-1.5 text-[11px] tracking-wide text-[var(--color-ink-3)] uppercase">
        {label}
      </div>
      <Link to={`/icerik/${contentId}`} className="block">
        <img
          src={api.imageUrl(contentId)}
          alt={label}
          className="aspect-4/3 w-full rounded-lg border border-[var(--color-line)] object-cover transition-colors hover:border-[#3a4250]"
        />
      </Link>
    </div>
  );
}

function Measure({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10.5px] tracking-wide text-[var(--color-ink-3)] uppercase">
        {label}
      </div>
      <div className="num text-[14px] text-[var(--color-ink)]">{value}</div>
    </div>
  );
}
