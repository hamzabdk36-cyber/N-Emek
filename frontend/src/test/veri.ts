/**
 * Test fiksturleri.
 *
 * Sentetik zincirler gercek demo verisinden bagimsiz tutuluyor: bir
 * yerlesim kurali kirildiginda "demo verisi degismis" mazereti
 * olmasin. Sekiller, uretimde gorulen dort duruma karsilik geliyor.
 */
import type {
  ChainEdgeView,
  ChainNodeView,
  Content,
  LabourCard,
  Party,
  User,
} from "../api";

export function dugum(
  id: string,
  depth: number,
  ek: Partial<ChainNodeView> = {},
): ChainNodeView {
  return {
    id,
    depth,
    role: depth === 0 ? "leaf" : "source",
    contributes: true,
    title: `${id} baslik`,
    owner: `${id} sahibi`,
    accent: "#5b8def",
    ...ek,
  };
}

export function kenar(
  id: string,
  from: string,
  to: string,
  ek: Partial<ChainEdgeView> = {},
): ChainEdgeView {
  return {
    id,
    from,
    to,
    stage: "geometry",
    stage_label: "Homografi + piksel doğrulaması",
    status: "confirmed",
    confidence: { level: "yuksek", score: 0.91, note: "ölçüldü" },
    visual_coverage: 0.84,
    source_usage: 0.9,
    mask_path: null,
    ...ek,
  };
}

export type Sekil = { nodes: ChainNodeView[]; edges: ChainEdgeView[] };

/** A -> B -> C, hepsi tek sutunda. Demo zincirinin sekli. */
export const DUZ_ZINCIR: Sekil = {
  nodes: [dugum("A", 2), dugum("B", 1), dugum("C", 0)],
  edges: [kenar("e-ab", "A", "B"), kenar("e-bc", "B", "C")],
};

/** A iki ayri turevi besliyor, ikisi de ayni yaprakta birlesiyor. */
export const ELMAS: Sekil = {
  nodes: [dugum("A", 2), dugum("B", 1), dugum("C", 1), dugum("D", 0)],
  edges: [
    kenar("e-ab", "A", "B"),
    kenar("e-ac", "A", "C", { visual_coverage: 0.41 }),
    kenar("e-bd", "B", "D"),
    kenar("e-cd", "C", "D", { visual_coverage: 0.19 }),
  ],
};

/** Bir satiri atlayan tek kenar; koridora cikmasi gereken durum. */
export const TEK_ATLAMA: Sekil = {
  nodes: [dugum("A", 2), dugum("B", 1), dugum("C", 0)],
  edges: [
    kenar("e-ab", "A", "B"),
    kenar("e-bc", "B", "C"),
    kenar("e-ac", "A", "C", { status: "proposed", visual_coverage: null }),
  ],
};

/** Iki ayri atlama kenari; ikisinin de kendi seridi olmali. */
export const IKI_ATLAMA: Sekil = {
  nodes: [dugum("A", 3), dugum("B", 2), dugum("C", 1), dugum("D", 0)],
  edges: [
    kenar("e-ab", "A", "B"),
    kenar("e-bc", "B", "C"),
    kenar("e-cd", "C", "D"),
    kenar("e-ac", "A", "C", { visual_coverage: null }),
    kenar("e-ad", "A", "D", { visual_coverage: 0.07 }),
  ],
};

export const SEKILLER: [string, Sekil][] = [
  ["düz zincir", DUZ_ZINCIR],
  ["elmas", ELMAS],
  ["tek atlama", TEK_ATLAMA],
  ["iki atlama", IKI_ATLAMA],
];

/* -------------------------------------------------------------------------- */
export function kullanici(ek: Partial<User> = {}): User {
  return {
    id: "u-ayse",
    handle: "ayse",
    display_name: "Ayşe Yıldız",
    accent: "#5b8def",
    role: "uye",
    ...ek,
  };
}

export function icerik(ek: Partial<Content> = {}): Content {
  return {
    id: "c-1",
    title: "Sabah ışığı",
    caption: "Kendi çektiğim kare.",
    width: 1024,
    height: 768,
    created_at: "2026-08-10T09:00:00",
    revenue: 1200,
    manifest_present: true,
    remix_allowed: true,
    owner: kullanici(),
    source_count: 0,
    derivative_count: 2,
    campaign_id: null,
    ...ek,
  };
}

function taraf(ek: Partial<Party> = {}): Party {
  return {
    role: "source",
    user_id: "u-ayse",
    user_name: "Ayşe Yıldız",
    content_id: "A",
    share: 0.12,
    share_pct: 12,
    amount: 129.6,
    factors: {
      kapsama: 0.84,
      toplam_kapsama: 0.97,
      guven: 0.91,
      derinlik: 2,
      sonumleme: 0.81,
      ham_agirlik: 0.619,
    },
    rules_applied: ["kaynak tabanı uygulandı"],
    evidence: [],
    edge_id: "e-ab",
    edge_status: "confirmed",
    disputable: true,
    ...ek,
  };
}

/**
 * Emek Karti fiksturu.
 *
 * Zincir DUZ_ZINCIR ile ayni kimlikleri kullaniyor ki grafik ve pay
 * satirlari ayni dugumlere baglansin - `ContentDetail` ikisini
 * `content_id` uzerinden esliyor.
 */
export function emekKarti(ek: Partial<LabourCard> = {}): LabourCard {
  return {
    content: {
      id: "C",
      title: "Şehir kolajı",
      caption: "Üç kareden birleştirdim.",
      width: 1200,
      height: 900,
      created_at: "2026-08-10T10:00:00",
      revenue: 1200,
      owner: {
        id: "u-ceyda",
        name: "Ceyda Arslan",
        handle: "ceyda",
        accent: "#b47ae0",
      },
      remix_allowed: true,
      min_source_share: 0,
    },
    provenance: {
      durum: "yeniden_kuruldu",
      incoming_manifest_present: false,
      manifest_present: true,
      manifest_urn: "urn:uuid:5f2c9a11-0000",
      watermark_tag: "NE-7F31",
      content_hash: "9c1f…a2",
      link_count: 1,
      confidence: { level: "yuksek", score: 0.91, note: "ölçüldü" },
      aciklama:
        "Yüklenen dosyada içerik kimliği yoktu; köken kanıtlardan yeniden kuruldu.",
    },
    chain: {
      nodes: [
        dugum("A", 2, { title: "Sabah ışığı", owner: "Ayşe Yıldız" }),
        dugum("B", 1, { title: "Kırpılmış kare", owner: "Burak Demir" }),
        dugum("C", 0, { title: "Şehir kolajı", owner: "Ceyda Arslan" }),
      ],
      edges: [kenar("e-ab", "A", "B"), kenar("e-bc", "B", "C")],
    },
    distribution: {
      gross_revenue: 1200,
      commission_amount: 120,
      distributable: 1080,
      parties: [
        taraf({
          role: "creator",
          user_id: "u-ceyda",
          user_name: "Ceyda Arslan",
          content_id: "C",
          share: 0.6,
          share_pct: 60,
          amount: 648,
          factors: { aciklama: "Üretici tabanı uygulandı." },
          edge_id: undefined,
          disputable: false,
        }),
        taraf({
          user_id: "u-burak",
          user_name: "Burak Demir",
          content_id: "B",
          share: 0.28,
          share_pct: 28,
          amount: 302.4,
          edge_id: "e-bc",
        }),
        taraf(),
        taraf({
          role: "platform",
          user_id: null,
          user_name: "Platform",
          content_id: null,
          share: 0,
          share_pct: 10,
          amount: 120,
          factors: {},
          rules_applied: [],
          edge_id: undefined,
          disputable: false,
        }),
      ],
    },
    rules: {
      label: "Varsayılan kural seti",
      commission: 0.1,
      creator_floor: 0.5,
      creator_ceiling: 0.9,
      source_floor: 0.05,
      chain_damping: 0.9,
      log: ["Komisyon %10 ayrıldı.", "Kaynak tabanı %5 kontrol edildi."],
    },
    campaign: null,
    ...ek,
  };
}
