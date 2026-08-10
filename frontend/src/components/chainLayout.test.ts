/**
 * Zincir yerlesiminin degismezleri.
 *
 * Buradaki asil iddia tek cumle: **hicbir kapsama rozeti hicbir dugum
 * kutusuyla ve hicbir baska rozetle kesismez.** 10 Agustos'ta demoda
 * gorulen hata tam olarak buydu ve kod okunarak bulunamamisti; sayisal
 * olarak sinanabilen tek yer burasi.
 */
import { describe, expect, it } from "vitest";
import {
  BADGE_H,
  NODE_H,
  NODE_W,
  badgeWidth,
  chainLayout,
  coverageLabel,
  overlaps,
} from "./chainLayout";
import { SEKILLER, TEK_ATLAMA, dugum, kenar } from "../test/veri";

describe("chainLayout — kesisme degismezleri", () => {
  it.each(SEKILLER)("%s: rozet hiçbir düğüm kutusuna binmiyor", (_ad, sekil) => {
    const { nodes, edges } = chainLayout(sekil.nodes, sekil.edges);

    for (const e of edges) {
      for (const n of nodes) {
        expect(
          overlaps(e.badge, n.box),
          `"${e.label}" rozeti (${e.edge.id}) "${n.node.id}" düğümüyle kesişiyor`,
        ).toBe(false);
      }
    }
  });

  it.each(SEKILLER)("%s: rozetler birbirine binmiyor", (_ad, sekil) => {
    const { edges } = chainLayout(sekil.nodes, sekil.edges);

    for (let i = 0; i < edges.length; i++) {
      for (let j = i + 1; j < edges.length; j++) {
        expect(
          overlaps(edges[i].badge, edges[j].badge),
          `${edges[i].edge.id} ve ${edges[j].edge.id} rozetleri üst üste`,
        ).toBe(false);
      }
    }
  });

  it.each(SEKILLER)("%s: her şey çizim alanının içinde kalıyor", (_ad, sekil) => {
    const layout = chainLayout(sekil.nodes, sekil.edges);

    for (const { badge, edge } of layout.edges) {
      expect(badge.x, `${edge.id} rozeti soldan taşıyor`).toBeGreaterThanOrEqual(0);
      expect(badge.x + badge.w, `${edge.id} rozeti sağdan taşıyor`).toBeLessThanOrEqual(
        layout.width,
      );
      expect(badge.y).toBeGreaterThanOrEqual(0);
      expect(badge.y + badge.h).toBeLessThanOrEqual(layout.height);
    }
    for (const { box, node } of layout.nodes) {
      expect(box.x + box.w, `${node.id} kutusu taşıyor`).toBeLessThanOrEqual(
        layout.width,
      );
      expect(box.y + box.h).toBeLessThanOrEqual(layout.height);
    }
  });
});

describe("chainLayout — koridor", () => {
  it("bir satırdan fazlasını atlayan kenar koridora çıkar, komşu kenarlar çıkmaz", () => {
    const { edges } = chainLayout(TEK_ATLAMA.nodes, TEK_ATLAMA.edges);
    const lane = new Map(edges.map((e) => [e.edge.id, e.lane]));

    expect(lane.get("e-ab")).toBeNull();
    expect(lane.get("e-bc")).toBeNull();
    expect(lane.get("e-ac")).toBe(0);
  });

  it("atlama kenarları ayrı şeritlere düşer ve kısa olan içeride kalır", () => {
    // A -> C (bir satir atlar) ve A -> D (iki satir atlar).
    const nodes = [dugum("A", 3), dugum("B", 2), dugum("C", 1), dugum("D", 0)];
    const edges = [kenar("uzun", "A", "D"), kenar("kisa", "A", "C")];

    const laid = chainLayout(nodes, edges);
    const at = new Map(laid.edges.map((e) => [e.edge.id, e]));

    expect(at.get("kisa")!.lane).toBe(0);
    expect(at.get("uzun")!.lane).toBe(1);
    // Serit 0 govdeye daha yakin; uzun kenar disa dusuyor ki seritler
    // birbirini kesmesin.
    expect(at.get("kisa")!.labelAt.x).toBeLessThan(at.get("uzun")!.labelAt.x);
  });

  it("koridor, en geniş rozete göre açılıyor", () => {
    // "olculemedi" rozeti sabit 30px serit araliginda sola tasip
    // aradaki dugum kutusunun uzerine biniyordu.
    const nodes = [dugum("A", 2), dugum("B", 1), dugum("C", 0)];
    const edges = [
      kenar("e-ab", "A", "B"),
      kenar("e-bc", "B", "C"),
      kenar("e-ac", "A", "C", { visual_coverage: null }),
    ];

    const laid = chainLayout(nodes, edges);
    const atlama = laid.edges.find((e) => e.edge.id === "e-ac")!;

    expect(atlama.label).toBe("ölçülemedi");
    for (const n of laid.nodes) {
      expect(overlaps(atlama.badge, n.box)).toBe(false);
    }
  });
});

describe("chainLayout — temel yerleşim", () => {
  it("boş zincirde çökmüyor", () => {
    expect(chainLayout([], [])).toEqual({
      width: 0,
      height: 0,
      nodes: [],
      edges: [],
    });
  });

  it("en derin kaynak en üstte, yaprak en altta", () => {
    const { nodes } = chainLayout(
      [dugum("A", 2), dugum("B", 1), dugum("C", 0)],
      [],
    );
    const y = new Map(nodes.map((n) => [n.node.id, n.at.y]));

    expect(y.get("A")!).toBeLessThan(y.get("B")!);
    expect(y.get("B")!).toBeLessThan(y.get("C")!);
  });

  it("aynı derinlikteki düğümler yan yana ve satır ortalanmış", () => {
    const { nodes } = chainLayout(
      [dugum("A", 2), dugum("B", 1), dugum("C", 1), dugum("D", 0)],
      [],
    );
    const at = new Map(nodes.map((n) => [n.node.id, n.at]));

    expect(at.get("B")!.y).toBe(at.get("C")!.y);
    expect(Math.abs(at.get("B")!.x - at.get("C")!.x)).toBeGreaterThanOrEqual(
      NODE_W,
    );
    // Tek dugumlu satir, iki dugumlu satirin ortasinda.
    const orta = (at.get("B")!.x + at.get("C")!.x + NODE_W) / 2;
    expect(at.get("A")!.x + NODE_W / 2).toBeCloseTo(orta, 6);
  });

  it("bilinmeyen düğüme giden kenar sessizce atlanıyor", () => {
    const { edges } = chainLayout(
      [dugum("A", 1), dugum("B", 0)],
      [kenar("var", "A", "B"), kenar("yok", "A", "HAYALET")],
    );

    expect(edges.map((e) => e.edge.id)).toEqual(["var"]);
  });

  it("düğüm kutusu ölçüleri çizimdeki sabitlerle aynı", () => {
    const { nodes } = chainLayout([dugum("A", 0)], []);
    expect(nodes[0].box).toMatchObject({ w: NODE_W, h: NODE_H });
  });
});

describe("rozet metni ve genişliği", () => {
  it("kapsama yüzdeye çevriliyor, ölçülemeyende metin yazıyor", () => {
    expect(coverageLabel(kenar("e", "A", "B", { visual_coverage: 0.84 }))).toBe(
      "%84",
    );
    expect(coverageLabel(kenar("e", "A", "B", { visual_coverage: null }))).toBe(
      "ölçülemedi",
    );
  });

  it("rozet metne göre genişliyor", () => {
    expect(badgeWidth("ölçülemedi")).toBeGreaterThan(badgeWidth("%84"));
    expect(badgeWidth("%9")).toBe(42);
  });

  it("rozet dikdörtgeni metnin merkezinde", () => {
    const { edges } = chainLayout(
      [dugum("A", 1), dugum("B", 0)],
      [kenar("e", "A", "B")],
    );
    const { badge, labelAt } = edges[0];

    expect(badge.x + badge.w / 2).toBeCloseTo(labelAt.x, 6);
    expect(badge.y + badge.h / 2).toBeCloseTo(labelAt.y, 6);
    expect(badge.h).toBe(BADGE_H);
  });
});
