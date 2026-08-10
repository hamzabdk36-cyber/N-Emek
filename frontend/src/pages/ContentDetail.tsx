/**
 * Gonderi detayi ve Emek Karti.
 *
 * Demonun kapak ekrani. Tek sayfada su soruya cevap verir:
 * "Bu icerik kazandi. Neden bana bu kadar geldi?"
 *
 * Sirasiyla: kokenin nasil belirlendigi -> pay dagilimi -> her payin
 * sayisal gerekcesi ve kaniti -> eslesen bolgenin gorseli -> zincir
 * -> uygulanan kurallar -> itiraz.
 */
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  api,
  money,
  pctRaw,
  type LabourCard,
  type Party,
} from "../api";
import { ChainGraph } from "../components/ChainGraph";
import { ImageCompare } from "../components/ImageCompare";
import { EvidenceList } from "../components/Pipeline";
import {
  Avatar,
  Badge,
  Button,
  ConfidenceBadge,
  ErrorNote,
  Field,
  Panel,
  ShareBar,
  Skeleton,
  Stat,
  inputClass,
  roleColor,
} from "../components/ui";
import { useSession } from "../session";

const DURUM_META: Record<
  string,
  { tone: "verify" | "gold" | "link" | "neutral"; label: string }
> = {
  yeniden_kuruldu: { tone: "gold", label: "Köken yeniden kuruldu" },
  kimlik_korundu: { tone: "verify", label: "İçerik kimliği korundu" },
  beyan_dogrulandi: { tone: "link", label: "Beyan ölçümle doğrulandı" },
  ozgun: { tone: "neutral", label: "Özgün içerik" },
};

export default function ContentDetail() {
  const { id = "" } = useParams();
  const { currentUser } = useSession();
  const [card, setCard] = useState<LabourCard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [revenueDraft, setRevenueDraft] = useState<string>("");

  const load = useCallback(() => {
    api
      .labourCard(id)
      .then((data) => {
        setCard(data);
        setRevenueDraft(String(data.content.revenue));
        const firstSource = data.distribution.parties.find(
          (p) => p.role === "source",
        );
        setSelectedSource((prev) => prev ?? firstSource?.content_id ?? null);
      })
      .catch((e: Error) => setError(e.message));
  }, [id]);

  useEffect(load, [load]);

  if (error) return <ErrorNote error={error} />;
  if (!card) return <EmekKartiIskeleti />;

  const { content, provenance, distribution, rules, chain, campaign } = card;
  const durum = DURUM_META[provenance.durum] ?? DURUM_META.ozgun;
  const sources = distribution.parties.filter((p) => p.role === "source");
  const selectedParty =
    sources.find((p) => p.content_id === selectedSource) ?? sources[0] ?? null;
  const selectedEdge = chain.edges.find(
    (e) => e.from === selectedParty?.content_id && e.to === content.id,
  );

  // Renk tutarliligi: pay seridi ve satirlar sirayla bir paletten renk
  // aliyordu, dolayisiyla Burak pay seridinde mor gorunurken avatarinda
  // ve zincir grafiginde maviydi. Ayni kisi her yerde ayni renk olsun
  // diye renk artik kullanicinin kendi vurgusundan geliyor.
  const accentOf = new Map(chain.nodes.map((n) => [n.id, n.accent]));
  const partyColor = (party: Party, index: number) =>
    (party.content_id && accentOf.get(party.content_id)) ||
    roleColor(party.role, index);

  return (
    <div className="space-y-5">
      {/* Baslik ------------------------------------------------------------ */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <Link
            to="/"
            className="text-[12px] text-[var(--color-ink-3)] hover:text-[var(--color-ink-2)]"
          >
            ← Akış
          </Link>
          <h1 className="mt-1 text-xl font-semibold tracking-tight">
            {content.title}
          </h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <Avatar name={content.owner.name} accent={content.owner.accent} size={22} />
            <span className="text-[13px] text-[var(--color-ink-2)]">
              {content.owner.name}
            </span>
            <Badge tone={durum.tone}>{durum.label}</Badge>
            {provenance.confidence && (
              <ConfidenceBadge band={provenance.confidence} />
            )}
          </div>
        </div>
        {content.remix_allowed && (
          <Link to={`/remix/${content.id}`}>
            <Button variant="primary">Remixle</Button>
          </Link>
        )}
      </div>

      {/* Koken anlatisi ---------------------------------------------------- */}
      <Panel title="Köken">
        <p className="text-[13.5px] leading-relaxed text-[var(--color-ink)]">
          {provenance.aciklama}
        </p>
        <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Stat
            label="Yüklenen dosyada kimlik"
            value={provenance.incoming_manifest_present ? "vardı" : "yoktu"}
            tone={provenance.incoming_manifest_present ? "verify" : "neutral"}
            sayisal={false}
          />
          <Stat
            label="Yayınlanan sürüm"
            value={provenance.manifest_present ? "imzalandı" : "imzasız"}
            hint={provenance.manifest_urn?.slice(0, 22)}
            sayisal={false}
          />
          <Stat label="Filigran kimliği" value={provenance.watermark_tag ?? "—"} />
          <Stat label="Bulunan bağ" value={provenance.link_count} />
        </div>
      </Panel>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
        {/* Sol: gorsel ve gelir -------------------------------------------- */}
        <div className="space-y-5">
          <Panel title="Görsel">
            <img
              src={api.imageUrl(content.id)}
              alt={content.title}
              className="w-full rounded-lg border border-[var(--color-line)]"
            />
            {content.caption && (
              <p className="mt-3 text-[13px] leading-relaxed text-[var(--color-ink-2)]">
                {content.caption}
              </p>
            )}
            <p className="num mt-2 text-[11px] text-[var(--color-ink-3)]">
              {content.width}×{content.height} · {provenance.content_hash}
            </p>
          </Panel>

          <Panel
            title="Gelir"
            subtitle="Demo için gönderinin ürettiği geliri değiştirip dağılımın nasıl değiştiğini görebilirsiniz."
          >
            <div className="flex gap-2">
              <input
                className={inputClass}
                value={revenueDraft}
                onChange={(e) => setRevenueDraft(e.target.value)}
                inputMode="decimal"
                aria-label="Gönderinin ürettiği gelir, TL"
              />
              <Button
                onClick={async () => {
                  await api.setRevenue(content.id, Number(revenueDraft) || 0);
                  load();
                }}
              >
                Uygula
              </Button>
            </div>
          </Panel>

          {campaign && (
            <Panel title="Kampanya">
              <p className="text-[13px] font-medium">{campaign.title}</p>
              <p className="mt-0.5 text-[12.5px] text-[var(--color-ink-2)]">
                {campaign.brand_name}
              </p>
              <div className="mt-3 grid grid-cols-2 gap-3">
                <Stat
                  label="Ödül havuzu"
                  value={money(campaign.reward_pool)}
                  tone="gold"
                />
                <Stat
                  label="Kaynak tabanı"
                  value={pctRaw(campaign.source_floor * 100, 0)}
                />
              </div>
            </Panel>
          )}
        </div>

        {/* Sag: Emek Karti -------------------------------------------------- */}
        <div className="space-y-5">
          {/* Brut gelir panel basliginin saginda da yaziyordu, hemen
              altindaki kutuda da. Ayni sayiyi iki kez gostermek panelin
              en ust satirini bos yere mesgul ediyordu; baslik artik
              kampanya kuralini tasiyor. */}
          <Panel title="Emek Kartı" subtitle={rules.label}>
            <div className="mb-4 grid grid-cols-3 gap-4">
              <Stat label="Brüt gelir" value={money(distribution.gross_revenue)} />
              <Stat
                label="Platform komisyonu"
                value={money(distribution.commission_amount)}
              />
              <Stat
                label="Dağıtılan"
                value={money(distribution.distributable)}
                tone="gold"
              />
            </div>

            <ShareBar
              segments={distribution.parties.map((p, i) => ({
                label: p.user_name,
                value: p.role === "platform" ? 0 : p.share,
                color: partyColor(p, i),
              }))}
            />

            <ul className="mt-4 space-y-2.5">
              {distribution.parties.map((party, i) => (
                <PartyRow
                  key={`${party.role}-${party.content_id ?? i}`}
                  party={party}
                  color={partyColor(party, i)}
                  selected={party.content_id === selectedParty?.content_id}
                  onSelect={() =>
                    party.content_id && setSelectedSource(party.content_id)
                  }
                  canDispute={
                    party.role === "source" &&
                    Boolean(party.edge_id) &&
                    party.user_id === currentUser?.id
                  }
                  onDisputed={load}
                />
              ))}
            </ul>

            {rules.log.length > 0 && (
              <div className="mt-4 rounded-lg border border-[var(--color-line-soft)] bg-[var(--color-surface-2)]/50 px-3.5 py-3">
                <p className="mb-1.5 text-[11px] tracking-wide text-[var(--color-ink-3)] uppercase">
                  Uygulanan kurallar
                </p>
                <ul className="space-y-1">
                  {rules.log.map((line, i) => (
                    <li
                      key={i}
                      className="text-[12.5px] leading-relaxed text-[var(--color-ink-2)]"
                    >
                      · {line}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Panel>

          {selectedParty?.content_id && (
            <Panel
              title="Ölçülen bölge"
              subtitle={`${selectedParty.user_name} adlı üreticinin içeriğinin bu gönderide kapladığı alan.`}
            >
              <ImageCompare
                sourceUrl={api.imageUrl(selectedParty.content_id)}
                derivativeUrl={api.imageUrl(content.id)}
                maskUrl={
                  selectedEdge?.mask_path && selectedEdge.id
                    ? api.maskUrl(selectedEdge.id)
                    : null
                }
                sourceLabel={selectedParty.user_name}
                derivativeLabel={content.title}
                coverage={selectedParty.factors.kapsama ?? null}
              />
              {selectedParty.evidence.length > 0 && (
                <div className="mt-4">
                  <p className="mb-2 text-[11px] tracking-wide text-[var(--color-ink-3)] uppercase">
                    Bu bağın kanıtları
                  </p>
                  <EvidenceList rows={selectedParty.evidence} />
                </div>
              )}
            </Panel>
          )}

          {chain.nodes.length > 1 && (
            <Panel
              title="Atıf zinciri"
              subtitle="Ok yönü türetme yönüdür. Kesikli çizgi, henüz onaylanmamış (önerilen) bağı gösterir."
            >
              <ChainGraph
                nodes={chain.nodes}
                edges={chain.edges}
                selectedId={selectedParty?.content_id ?? null}
                onSelect={(nodeId) =>
                  nodeId !== content.id && setSelectedSource(nodeId)
                }
              />
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
function PartyRow({
  party,
  color,
  selected,
  onSelect,
  canDispute,
  onDisputed,
}: {
  party: Party;
  color: string;
  selected: boolean;
  onSelect: () => void;
  canDispute: boolean;
  onDisputed: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const isSource = party.role === "source";
  const f = party.factors;

  return (
    <li
      className={`rounded-lg border transition-colors ${
        selected
          ? "border-[#3a4250] bg-[var(--color-surface-2)]"
          : "border-[var(--color-line-soft)] bg-[var(--color-surface-2)]/40"
      }`}
    >
      <div className="flex items-center gap-3 px-3.5 py-2.5">
        <span
          className="h-8 w-1 shrink-0 rounded-full"
          style={{ background: color }}
          aria-hidden
        />
        <button
          type="button"
          onClick={() => {
            onSelect();
            setExpanded((v) => !v);
          }}
          className="min-w-0 flex-1 text-left"
          aria-expanded={expanded}
        >
          <span className="flex items-center gap-2">
            <span className="truncate text-[13.5px] font-medium">
              {party.user_name}
            </span>
            <RoleBadge role={party.role} />
          </span>
          {isSource && f.derinlik != null && (
            <span className="num mt-0.5 block text-[11.5px] text-[var(--color-ink-3)]">
              zincirde {f.derinlik} adım geride · kendi kattığı alan{" "}
              {pctRaw((f.kapsama ?? 0) * 100)}
              {f.toplam_kapsama != null &&
                ` · toplam görünen ${pctRaw(f.toplam_kapsama * 100)}`}
            </span>
          )}
        </button>
        <div className="shrink-0 text-right">
          <div className="num text-[14px] font-semibold text-[var(--color-gold)]">
            {money(party.amount)}
          </div>
          <div className="num text-[11.5px] text-[var(--color-ink-3)]">
            {pctRaw(party.share_pct)}
          </div>
        </div>
      </div>

      {expanded && (
        <div className="fade-in space-y-3 border-t border-[var(--color-line-soft)] px-3.5 py-3">
          {isSource && (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <MiniStat label="kapsama" value={pctRaw((f.kapsama ?? 0) * 100)} />
              <MiniStat label="güven" value={(f.guven ?? 0).toFixed(2)} />
              <MiniStat label="sönümleme" value={(f.sonumleme ?? 1).toFixed(2)} />
              <MiniStat
                label="ham ağırlık"
                value={(f.ham_agirlik ?? 0).toFixed(3)}
              />
            </div>
          )}
          {isSource && (
            <p className="num text-[11.5px] leading-relaxed text-[var(--color-ink-3)]">
              pay = kapsama {pctRaw((f.kapsama ?? 0) * 100)} × güven{" "}
              {(f.guven ?? 0).toFixed(2)} × sönümleme{" "}
              {(f.sonumleme ?? 1).toFixed(2)} = {(f.ham_agirlik ?? 0).toFixed(3)}
            </p>
          )}
          {party.rules_applied.length > 0 && (
            <ul className="space-y-1">
              {party.rules_applied.map((rule, i) => (
                <li
                  key={i}
                  className="text-[12px] leading-relaxed text-[var(--color-ink-2)]"
                >
                  · {rule}
                </li>
              ))}
            </ul>
          )}
          {f.aciklama && (
            <p className="text-[12px] text-[var(--color-ink-2)]">{f.aciklama}</p>
          )}
          {party.evidence.length > 0 && (
            <EvidenceList rows={party.evidence} compact />
          )}
          {canDispute && party.edge_id && (
            <DisputeBox edgeId={party.edge_id} onDone={onDisputed} />
          )}
        </div>
      )}
    </li>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10px] tracking-wide text-[var(--color-ink-3)] uppercase">
        {label}
      </div>
      <div className="num text-[13px] text-[var(--color-ink)]">{value}</div>
    </div>
  );
}

function RoleBadge({ role }: { role: string }) {
  if (role === "creator") return <Badge tone="gold">üretici</Badge>;
  if (role === "platform") return <Badge tone="neutral">platform</Badge>;
  return <Badge tone="link">kaynak</Badge>;
}

/* -------------------------------------------------------------------------- */
function DisputeBox({ edgeId, onDone }: { edgeId: string; onDone: () => void }) {
  const { currentUser } = useSession();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState(
    "Orijinalimin daha geniş bir bölümü kullanılmış; pay düşük hesaplandı.",
  );
  const [busy, setBusy] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!currentUser) return null;

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const dispute = await api.openDispute(edgeId, currentUser!.id, reason);
      const outcome = await api.resolveDispute(dispute.id);
      setSummary(outcome.summary);
      onDone();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (summary) {
    return (
      <div className="rounded-lg border border-[var(--color-link)]/40 bg-[var(--color-link-dim)]/40 px-3.5 py-2.5 text-[12.5px] leading-relaxed text-[var(--color-ink)]">
        {summary}
      </div>
    );
  }

  return (
    <div className="border-t border-[var(--color-line-soft)] pt-3">
      {!open ? (
        <Button variant="danger" onClick={() => setOpen(true)}>
          Bu paya itiraz et
        </Button>
      ) : (
        <div className="space-y-2.5">
          <Field
            label="İtiraz gerekçesi"
            hint="İtiraz, bağı daha hassas bir dedektörle (SIFT) yeniden ölçtürür. Sonuç değişirse tüm zincirin payları güncellenir."
          >
            <textarea
              className={`${inputClass} min-h-20 resize-y`}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </Field>
          {error && <ErrorNote error={error} />}
          <div className="flex gap-2">
            <Button variant="primary" onClick={submit} disabled={busy}>
              {busy ? "Yeniden ölçülüyor…" : "İtirazı gönder"}
            </Button>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Vazgeç
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Emek Karti yuklenirken sayfanin yerlesimini onceden cizer.
 *
 * Bu ekran demonun kapak karesi ve hesabi (zincir yurutme + pay
 * dagilimi) sunucuda birkac milisaniye suruyor; yine de bos ekrandan
 * ani sicrama urunu yarim gosteriyordu. Iskelet gercek duzeni taklit
 * ediyor: baslik, koken kutusu, solda gorsel, sagda pay dagilimi.
 */
function EmekKartiIskeleti() {
  return (
    <div className="space-y-5">
      <span className="sr-only" role="status">
        Emek Kartı hesaplanıyor
      </span>
      <div className="space-y-2">
        <Skeleton className="h-7 w-64" />
        <Skeleton className="h-5 w-80" gecikme={60} />
      </div>
      <Panel title="Köken">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-3 w-24" gecikme={i * 60} />
              <Skeleton className="h-6 w-32" gecikme={i * 60 + 30} />
            </div>
          ))}
        </div>
      </Panel>
      <div className="grid gap-5 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
        <Panel title="Görsel">
          <Skeleton className="aspect-4/3 w-full" />
        </Panel>
        <Panel title="Emek Kartı">
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              {[0, 1, 2].map((i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-3 w-20" gecikme={i * 60} />
                  <Skeleton className="h-6 w-24" gecikme={i * 60 + 30} />
                </div>
              ))}
            </div>
            <Skeleton className="h-2.5 w-full" gecikme={180} />
            {[0, 1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-14 w-full" gecikme={220 + i * 70} />
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
