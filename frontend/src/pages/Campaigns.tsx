/**
 * Marka kampanya paneli.
 *
 * Is modelinin somut karsiligi: marka bir odul havuzu koyar, paylasim
 * kurallarini belirler, kampanya sonunda havuz katilan gonderilere ve
 * onlarin atif zincirlerine dagitilir. Platform kampanya yonetimi ve
 * analiz hizmetinden komisyon alir.
 */
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  api,
  money,
  pctRaw,
  type Campaign,
  type CampaignDistribution,
} from "../api";
import {
  Badge,
  Button,
  ErrorNote,
  Field,
  Panel,
  ShareBar,
  Spinner,
  Stat,
  inputClass,
  roleColor,
} from "../components/ui";

export default function Campaigns() {
  const [items, setItems] = useState<Campaign[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [distribution, setDistribution] = useState<CampaignDistribution | null>(
    null,
  );
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(() => {
    api
      .campaigns()
      .then(setItems)
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(load, [load]);

  async function distribute(id: string) {
    setBusy(id);
    setError(null);
    try {
      setDistribution(await api.distributeCampaign(id));
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Kampanyalar</h1>
          <p className="mt-1 max-w-2xl text-[13px] leading-relaxed text-[var(--color-ink-2)]">
            Markalar remix kampanyaları için ödül havuzu oluşturur. Havuz
            dağıtılırken her gönderinin payı kendi atıf zincirine, ölçülmüş
            katkı oranlarına göre bölünür.
          </p>
        </div>
        <Button
          variant={showForm ? "default" : "primary"}
          onClick={() => setShowForm((v) => !v)}
        >
          {showForm ? "Kapat" : "Kampanya oluştur"}
        </Button>
      </div>

      {error && <ErrorNote error={error} />}
      {showForm && (
        <CampaignForm
          onDone={() => {
            setShowForm(false);
            load();
          }}
        />
      )}

      {!items && !error && <Spinner label="Kampanyalar yükleniyor…" />}

      <div className="grid gap-4 md:grid-cols-2">
        {items?.map((campaign) => (
          <Panel
            key={campaign.id}
            title={campaign.brand_name}
            subtitle={campaign.title}
            right={
              <Badge tone={campaign.status === "distributed" ? "verify" : "gold"}>
                {campaign.status === "distributed" ? "dağıtıldı" : "aktif"}
              </Badge>
            }
          >
            {campaign.brief && (
              <p className="mb-3 text-[13px] leading-relaxed text-[var(--color-ink-2)]">
                {campaign.brief}
              </p>
            )}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Stat
                label="Ödül havuzu"
                value={money(campaign.reward_pool)}
                tone="gold"
              />
              <Stat label="Katılan gönderi" value={campaign.content_count ?? 0} />
              <Stat
                label="Kaynak tabanı"
                value={pctRaw(campaign.source_floor * 100, 0)}
                hint="kaynaklara asgari"
              />
              <Stat
                label="Komisyon"
                value={pctRaw(campaign.commission * 100, 0)}
              />
            </div>
            <Button
              className="mt-4 w-full"
              variant="primary"
              disabled={busy === campaign.id}
              onClick={() => distribute(campaign.id)}
            >
              {busy === campaign.id
                ? "Zincirler hesaplanıyor…"
                : "Havuzu dağıt"}
            </Button>
          </Panel>
        ))}
      </div>

      {distribution && <DistributionReport data={distribution} />}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
function DistributionReport({ data }: { data: CampaignDistribution }) {
  return (
    <Panel
      title="Dağıtım raporu"
      subtitle="Havuz önce gönderiler arasında bölündü, sonra her gönderinin payı kendi atıf zincirine dağıtıldı."
    >
      <div className="mb-4 grid grid-cols-3 gap-4">
        <Stat label="Ödül havuzu" value={money(data.reward_pool)} tone="gold" />
        <Stat label="Üreticilere" value={money(data.total_paid)} tone="verify" />
        <Stat label="Platform payı" value={money(data.platform_total)} />
      </div>

      <ul className="space-y-3">
        {data.per_content.map((row) => (
          <li
            key={row.content_id}
            className="rounded-lg border border-[var(--color-line-soft)] bg-[var(--color-surface-2)]/50 p-3.5"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Link
                to={`/icerik/${row.content_id}`}
                className="text-[13.5px] font-medium hover:text-[var(--color-gold)]"
              >
                {row.title}
              </Link>
              <div className="text-right">
                <div className="num text-[13.5px] font-semibold text-[var(--color-gold)]">
                  {money(row.allocation)}
                </div>
                <div className="text-[11px] text-[var(--color-ink-3)]">
                  ağırlık {pctRaw(row.weight * 100)} · {row.basis}
                </div>
              </div>
            </div>

            <div className="mt-3">
              <ShareBar
                segments={row.parties.map((p, i) => ({
                  label: p.user_name,
                  value: p.role === "platform" ? 0 : p.share_pct,
                  color: roleColor(p.role, i),
                }))}
              />
            </div>

            <ul className="mt-2.5 grid gap-1.5 sm:grid-cols-2">
              {row.parties.map((p, i) => (
                <li
                  key={i}
                  className="flex items-center justify-between gap-2 text-[12.5px]"
                >
                  <span className="flex min-w-0 items-center gap-2">
                    <span
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{ background: roleColor(p.role, i) }}
                    />
                    <span className="truncate text-[var(--color-ink-2)]">
                      {p.user_name}
                    </span>
                  </span>
                  <span className="num shrink-0 text-[var(--color-ink)]">
                    {pctRaw(p.share_pct)} · {money(p.amount)}
                  </span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </Panel>
  );
}

/* -------------------------------------------------------------------------- */
function CampaignForm({ onDone }: { onDone: () => void }) {
  const [brand, setBrand] = useState("");
  const [title, setTitle] = useState("");
  const [brief, setBrief] = useState("");
  const [pool, setPool] = useState(50000);
  const [sourceFloor, setSourceFloor] = useState(15);
  const [commission, setCommission] = useState(10);
  const [ceiling, setCeiling] = useState(80);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      await api.createCampaign({
        brand_name: brand,
        title,
        brief,
        reward_pool: pool,
        commission: commission / 100,
        source_floor: sourceFloor / 100,
        creator_ceiling: ceiling / 100,
      });
      onDone();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Panel
      title="Yeni kampanya"
      subtitle="Belirlediğiniz paylaşım kuralları, kampanyaya katılan tüm gönderilerin Emek Kartlarında görünür."
    >
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <Field label="Marka">
            <input
              className={inputClass}
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              placeholder="Anadolu Kahve"
            />
          </Field>
          <Field label="Kampanya başlığı">
            <input
              className={inputClass}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Şehrin Renkleri Remix Kampanyası"
            />
          </Field>
          <Field label="Brief">
            <textarea
              className={`${inputClass} min-h-20 resize-y`}
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
            />
          </Field>
          <Field label="Ödül havuzu (TL)">
            <input
              className={inputClass}
              value={pool}
              inputMode="numeric"
              onChange={(e) => setPool(Number(e.target.value) || 0)}
            />
          </Field>
        </div>

        <div className="space-y-3">
          <Field
            label={`Kaynak tabanı: %${sourceFloor}`}
            hint="Kaynaklara ayrılacak asgari toplam pay."
          >
            <input
              type="range"
              min={0}
              max={50}
              value={sourceFloor}
              onChange={(e) => setSourceFloor(Number(e.target.value))}
              className="w-full accent-[var(--color-gold)]"
            />
          </Field>
          <Field
            label={`Üretici tavanı: %${ceiling}`}
            hint="Kaynak varken son üreticinin alabileceği en yüksek pay."
          >
            <input
              type="range"
              min={50}
              max={100}
              value={ceiling}
              onChange={(e) => setCeiling(Number(e.target.value))}
              className="w-full accent-[var(--color-gold)]"
            />
          </Field>
          <Field
            label={`Platform komisyonu: %${commission}`}
            hint="Kampanya yönetimi ve analiz hizmeti karşılığı."
          >
            <input
              type="range"
              min={0}
              max={30}
              value={commission}
              onChange={(e) => setCommission(Number(e.target.value))}
              className="w-full accent-[var(--color-gold)]"
            />
          </Field>
          {error && <ErrorNote error={error} />}
          <Button
            variant="primary"
            onClick={submit}
            disabled={busy || !brand || !title || pool <= 0}
            className="w-full"
          >
            {busy ? "Oluşturuluyor…" : "Kampanyayı oluştur"}
          </Button>
        </div>
      </div>
    </Panel>
  );
}
