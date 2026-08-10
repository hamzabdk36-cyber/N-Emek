/**
 * Backend istemcisi.
 *
 * Tum tipler backend'deki `app/api/schemas.py` ile birebir eslesir.
 * Sozlesme degistiginde iki taraf birlikte guncellenir.
 */

const BASE = "/api";

/* -------------------------------------------------------------------------- */
/* Oturum jetonu                                                               */
/* -------------------------------------------------------------------------- */
/**
 * Jeton modul duzeyinde tutuluyor, React durumunda degil: `api.*`
 * cagrilari bilesen agacinin disindan da yapilabiliyor ve her cagriya
 * jetonu elle gecirmek her uc icin bir parametre daha demekti.
 *
 * `localStorage`'a yazilmiyor. Demo kimlik saglayicisi zaten parolasiz
 * ve jeton kisa omurlu; kalici saklamak, sayfa yenilendiginde suresi
 * dolmus bir jetonla acilmaya calismak disinda bir sey kazandirmiyor.
 * Sayfa yenilenince oturum bastan aciliyor (bkz. session.tsx).
 */
let token: string | null = null;

export function setToken(next: string | null) {
  token = next;
}

/** Jeton suresi dolduysa oturumu yeniden acmak icin; session.tsx kuruyor. */
let onUnauthorized: (() => Promise<boolean>) | null = null;

export function setUnauthorizedHandler(handler: (() => Promise<boolean>) | null) {
  onUnauthorized = handler;
}

function withAuth(init?: RequestInit): RequestInit {
  if (!token) return init ?? {};
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${token}`);
  return { ...init, headers };
}

async function req<T>(path: string, init?: RequestInit, retry = true): Promise<T> {
  const res = await fetch(BASE + path, withAuth(init));

  // Jetonun suresi dolmus ya da sunucu yeniden baslamis olabilir
  // (imzalama anahtari surec basina uretiliyor). Oturumu sessizce
  // yenileyip bir kez daha deniyoruz - kullanici demonun ortasinda
  // "oturum acin" duvarina toslamasin.
  if (res.status === 401 && retry && onUnauthorized) {
    const yenilendi = await onUnauthorized();
    if (yenilendi) return req<T>(path, init, false);
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* govde JSON degilse durum metnini kullan */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

/* -------------------------------------------------------------------------- */
/* Tipler                                                                      */
/* -------------------------------------------------------------------------- */
export interface User {
  id: string;
  handle: string;
  display_name: string;
  accent: string;
}

export interface Content {
  id: string;
  title: string;
  caption: string;
  width: number;
  height: number;
  created_at: string;
  revenue: number;
  manifest_present: boolean;
  remix_allowed: boolean;
  owner: User;
  source_count: number;
  derivative_count: number;
  campaign_id: string | null;
}

export interface StageLog {
  stage: string;
  found: boolean;
  detail: string;
  aciklama: string;
}

export interface EvidenceItem {
  stage: string;
  found?: boolean;
  matched?: boolean;
  aciklama?: string;
  [key: string]: unknown;
}

export interface RecoveredLink {
  parent_content_id: string;
  parent_title: string;
  stage: string;
  stage_label: string;
  confidence: number;
  confidence_level: string;
  visual_coverage: number | null;
  source_usage: number | null;
  geometry_verified: boolean;
  evidence: EvidenceItem[];
}

export interface RecoveryResult {
  manifest_present: boolean;
  manifest_urn: string | null;
  watermark_tag: string | null;
  links: RecoveredLink[];
  stage_log: StageLog[];
  timings_ms: Record<string, number>;
}

export interface IngestResult {
  content: Content;
  recovery: RecoveryResult;
}

export interface ConfidenceBand {
  level: "yuksek" | "orta" | "dusuk";
  score: number;
  note: string;
}

export interface EvidenceRow {
  stage: string;
  label: string;
  found: boolean;
  aciklama: string;
  detay: Record<string, unknown>;
}

export interface Party {
  role: "creator" | "source" | "platform";
  user_id: string | null;
  user_name: string;
  content_id: string | null;
  share: number;
  share_pct: number;
  amount: number;
  factors: {
    kapsama?: number;
    toplam_kapsama?: number | null;
    guven?: number;
    derinlik?: number;
    sonumleme?: number;
    ham_agirlik?: number;
    notlar?: string[];
    aciklama?: string;
  };
  rules_applied: string[];
  evidence: EvidenceRow[];
  edge_id?: string;
  edge_status?: string;
  disputable?: boolean;
}

export interface ChainNodeView {
  id: string;
  depth: number;
  role: "leaf" | "source";
  /** false = zincirde ara halka ama katkisi pay esiginin altinda. */
  contributes: boolean;
  title: string;
  owner: string;
  accent: string;
}

export interface ChainEdgeView {
  id: string;
  from: string;
  to: string;
  stage: string;
  stage_label: string;
  status: string;
  confidence: ConfidenceBand;
  visual_coverage: number | null;
  source_usage: number | null;
  mask_path: string | null;
}

export interface LabourCard {
  content: {
    id: string;
    title: string;
    caption: string;
    width: number;
    height: number;
    created_at: string;
    revenue: number;
    owner: { id: string; name: string; handle: string; accent: string };
    remix_allowed: boolean;
    min_source_share: number;
  };
  provenance: {
    durum: "yeniden_kuruldu" | "kimlik_korundu" | "beyan_dogrulandi" | "ozgun";
    incoming_manifest_present: boolean;
    manifest_present: boolean;
    manifest_urn: string | null;
    watermark_tag: string | null;
    content_hash: string;
    link_count: number;
    confidence: ConfidenceBand | null;
    aciklama: string;
  };
  chain: { nodes: ChainNodeView[]; edges: ChainEdgeView[] };
  distribution: {
    gross_revenue: number;
    commission_amount: number;
    distributable: number;
    parties: Party[];
  };
  rules: {
    label: string;
    commission: number;
    creator_floor: number;
    creator_ceiling: number;
    source_floor: number;
    chain_damping: number;
    log: string[];
  };
  campaign: Campaign | null;
}

export interface Campaign {
  id: string;
  brand_name: string;
  title: string;
  brief: string;
  reward_pool: number;
  status: string;
  commission: number;
  source_floor: number;
  creator_ceiling: number;
  content_count?: number;
}

export interface CampaignDistribution {
  campaign_id: string;
  reward_pool: number;
  total_paid: number;
  platform_total: number;
  per_content: {
    content_id: string;
    title: string;
    weight: number;
    basis: string;
    allocation: number;
    parties: { role: string; user_name: string; share_pct: number; amount: number }[];
  }[];
}

export interface DisputeQueueItem {
  id: string;
  status: string;
  reason: string;
  raiser: string;
  created_at: string;
  edge: {
    id: string | null;
    child_id: string | null;
    parent_id: string | null;
    confidence: number | null;
    visual_coverage: number | null;
  };
  resolution: Record<string, unknown>;
}

export interface Health {
  status: string;
  indexed_contents: number;
  device: string;
  c2pa_signing: boolean;
}

/** `POST /api/oturum` yaniti - demo kimlik sağlayıcısı. */
export interface Oturum {
  token: string;
  /** Unix saniye. */
  expires_at: number;
  user: User;
}

/* -------------------------------------------------------------------------- */
/* Uclar                                                                       */
/* -------------------------------------------------------------------------- */
export const api = {
  health: () => req<Health>("/health"),
  users: () => req<User[]>("/users"),

  /**
   * Demo kimlik sağlayıcısı: kullanıcı kimliğini imzalı, kısa ömürlü
   * bir jetona çevirir. Parola sorulmaz — kimlik doğrulama ana
   * platformun işi; gerekçe `backend/app/core/security.py` içinde.
   */
  oturum: (userId: string) =>
    req<Oturum>("/oturum", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    }),
  earnings: (userId: string) =>
    req<{ user_id: string; total: number; as_creator: number; as_source: number; payout_count: number }>(
      `/users/${userId}/earnings`,
    ),

  feed: () => req<Content[]>("/feed"),
  content: (id: string) => req<Content>(`/contents/${id}`),
  imageUrl: (id: string) => `${BASE}/contents/${id}/image`,
  maskUrl: (edgeId: string) => `${BASE}/edges/${edgeId}/mask`,

  labourCard: (id: string) => req<LabourCard>(`/contents/${id}/labour-card`),

  upload: (form: FormData) =>
    req<IngestResult>("/contents", { method: "POST", body: form }),
  remix: (parentId: string, form: FormData) =>
    req<IngestResult>(`/contents/${parentId}/remix`, { method: "POST", body: form }),
  verify: (form: FormData) =>
    req<RecoveryResult>("/verify", { method: "POST", body: form }),

  setRevenue: (id: string, amount: number) =>
    req<{ content_id: string; revenue: number }>(`/contents/${id}/revenue`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount }),
    }),
  distribute: (id: string) =>
    req<Record<string, unknown>>(`/contents/${id}/distribute`, { method: "POST" }),

  campaigns: () => req<Campaign[]>("/campaigns"),
  createCampaign: (body: Omit<Campaign, "id" | "status" | "content_count">) =>
    req<Campaign>("/campaigns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  distributeCampaign: (id: string) =>
    req<CampaignDistribution>(`/campaigns/${id}/distribute`, { method: "POST" }),

  // İtirazı kimin açtığı gövdeden değil jetondan okunuyor; uç,
  // payın sahibi olmayan birine 403 döner.
  openDispute: (edgeId: string, reason: string) =>
    req<{ id: string; status: string }>("/disputes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ edge_id: edgeId, reason }),
    }),
  resolveDispute: (id: string) =>
    req<{ id: string; status: string; changed: boolean; summary: string; resolution: Record<string, unknown> }>(
      `/disputes/${id}/resolve`,
      { method: "POST" },
    ),
  disputeQueue: () => req<DisputeQueueItem[]>("/disputes/queue"),
  moderate: (id: string, accept: boolean, note: string) =>
    req<Record<string, unknown>>(`/disputes/${id}/moderate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ accept, note }),
    }),
};

/* -------------------------------------------------------------------------- */
/* Bicimlendirme                                                               */
/* -------------------------------------------------------------------------- */
const TRY = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  maximumFractionDigits: 2,
});

export const money = (value: number) => TRY.format(value);

/**
 * Ondalik ayraci virgul.
 *
 * `Intl` yerine dize degisimi: basamak sayisi cagri basina degisiyor ve
 * her cagride yeni bir bicimlendirici kurmak gereksiz. Onemli olan
 * ayracin *tek yerde* tanimli olmasi - onceki surumde `ShareBar` bunu
 * kendi icinde yapiyordu, geri kalan bes ekran ise noktali yaziyordu.
 */
const virgul = (text: string) => text.replace(".", ",");

/** Oran (0–1) -> yuzde metni. Ornek: 0.84 -> "%84,0" */
export const pct = (value: number, digits = 1) =>
  `%${virgul((value * 100).toFixed(digits))}`;

/** Hazir yuzde degeri -> yuzde metni. Ornek: 84 -> "%84,0" */
export const pctRaw = (value: number, digits = 1) =>
  `%${virgul(value.toFixed(digits))}`;

/**
 * Ondalikli sayi -> Turkce metin. Ornek: 0.91 -> "0,91"
 *
 * Guven, sonumleme ve ham agirlik gibi olcum degerleri icin. Bunlar
 * yuzde degil, dolayisiyla `pctRaw` uygun degil; ama ayni imla kurali
 * gecerli - ekranda "0.91" yaziyorsa kural ciğnenmis oluyor.
 */
export const sayi = (value: number, digits = 2) => virgul(value.toFixed(digits));
