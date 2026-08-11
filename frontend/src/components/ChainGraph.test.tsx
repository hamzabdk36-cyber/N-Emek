/**
 * Zincir grafiginin cizimi.
 *
 * Yerlesim aritmetigi `chainLayout.test.ts` icinde sinaniyor; burada
 * sinanan sey, ekranda okunan *anlam*: pay esiginin altinda kalan ara
 * halka grafikten dusmuyor, kesikli ciziliyor ve neden pay almadigi
 * yaziyor.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ChainGraph } from "./ChainGraph";
import { DUZ_ZINCIR, dugum, kenar } from "../test/veri";

describe("ChainGraph", () => {
  it("boş zincir hiçbir şey çizmiyor", () => {
    const { container } = render(<ChainGraph nodes={[]} edges={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("her düğüm ve her kenar için birer öğe çiziyor", () => {
    const { container } = render(
      <ChainGraph nodes={DUZ_ZINCIR.nodes} edges={DUZ_ZINCIR.edges} />,
    );

    expect(screen.getByRole("img", { name: /^Atıf zinciri, 3 halka\./ })).toBeVisible();
    // Kenar basina bir <path>; ok isaretcisinin kendi <path>'i <defs>
    // icinde oldugu icin disarida sayilmiyor.
    expect(container.querySelectorAll("g[fill='none'] > path")).toHaveLength(2);
    for (const node of DUZ_ZINCIR.nodes) {
      expect(screen.getByText(node.title)).toBeInTheDocument();
      expect(screen.getByText(node.owner)).toBeInTheDocument();
    }
  });

  it("yaprak YAYINLANAN, kaynaklar kaç adım geride yazıyor", () => {
    render(<ChainGraph nodes={DUZ_ZINCIR.nodes} edges={DUZ_ZINCIR.edges} />);

    expect(screen.getByText("YAYINLANAN")).toBeInTheDocument();
    expect(screen.getByText("2 ADIM GERİDE")).toBeInTheDocument();
    expect(screen.getByText("1 ADIM GERİDE")).toBeInTheDocument();
  });

  it("pay eşiğinin altındaki ara halka kesikli çiziliyor ve payı olmadığı yazıyor", () => {
    const nodes = [
      dugum("A", 2),
      dugum("B", 1, { contributes: false }),
      dugum("C", 0),
    ];
    const { container } = render(
      <ChainGraph nodes={nodes} edges={DUZ_ZINCIR.edges} />,
    );

    // Dugum grafikten dusmuyor.
    expect(screen.getByText("ARA HALKA · PAY YOK")).toBeInTheDocument();
    expect(screen.queryByText("1 ADIM GERİDE")).not.toBeInTheDocument();

    const kutu = container.querySelector<SVGRectElement>(
      "rect[stroke-dasharray='4 3']",
    );
    expect(kutu, "katkısız düğümün kutusu kesikli olmalı").not.toBeNull();
    expect(Number(kutu!.getAttribute("opacity"))).toBeLessThan(1);
    // Katkisi olan dugumler duz cizgiyle kaliyor - kesikli olan yalnizca bir tane.
    expect(container.querySelectorAll("rect[stroke-dasharray='4 3']")).toHaveLength(
      1,
    );
  });

  it("onaylanmamış bağ kesikli çizgiyle gösteriliyor", () => {
    const edges = [
      kenar("e-ab", "A", "B", { status: "proposed" }),
      kenar("e-bc", "B", "C"),
    ];
    const { container } = render(
      <ChainGraph nodes={DUZ_ZINCIR.nodes} edges={edges} />,
    );

    const yollar = [...container.querySelectorAll("g[fill='none'] > path")];
    const kesikli = yollar.filter((p) => p.getAttribute("stroke-dasharray"));
    expect(kesikli).toHaveLength(1);
  });

  it("kapsama rozetleri ölçülen değeri yazıyor", () => {
    render(
      <ChainGraph
        nodes={DUZ_ZINCIR.nodes}
        edges={[
          kenar("e-ab", "A", "B", { visual_coverage: 0.84 }),
          kenar("e-bc", "B", "C", { visual_coverage: null }),
        ]}
      />,
    );

    expect(screen.getByText("%84")).toBeInTheDocument();
    expect(screen.getByText("ölçülemedi")).toBeInTheDocument();
  });

  /**
   * Grafik bilgiyi yalnizca *cizimle* tasiyor; gorsel olmayan
   * kullanicinin zinciri ogrenebilecegi tek yer `aria-label`. Onceden
   * orada yalnizca "İçerik atıf zinciri" yaziyordu - yani kim kimden
   * turemis, hangi oranda, hicbiri ulasmiyordu. `ShareBar` ile ayni
   * desen (ERISILEBILIRLIK.md §5).
   */
  describe("metin karşılığı", () => {
    const ad = () => screen.getByRole("img").getAttribute("aria-label")!;

    it("zincirin tamamını yapraktan kökene anlatıyor", () => {
      render(<ChainGraph nodes={DUZ_ZINCIR.nodes} edges={DUZ_ZINCIR.edges} />);

      expect(ad()).toBe(
        "Atıf zinciri, 3 halka. " +
          "C baslik — C sahibi, yayınlanan. " +
          "Kaynağı: B baslik — B sahibi, 1 adım geride, kullanılan alan %84,0. " +
          "Onun kaynağı: A baslik — A sahibi, 2 adım geride, kullanılan alan %84,0.",
      );
    });

    it("ölçülemeyen alanı gizlemiyor", () => {
      render(
        <ChainGraph
          nodes={DUZ_ZINCIR.nodes}
          edges={[
            kenar("e-ab", "A", "B", { visual_coverage: null }),
            kenar("e-bc", "B", "C"),
          ]}
        />,
      );
      expect(ad()).toContain("kullanılan alan ölçülemedi");
    });

    it("payı olmayan ara halkayı da söylüyor", () => {
      render(
        <ChainGraph
          nodes={[dugum("A", 2), dugum("B", 1, { contributes: false }), dugum("C", 0)]}
          edges={DUZ_ZINCIR.edges}
        />,
      );
      expect(ad()).toContain("1 adım geride, ara halka, payı yok");
    });

    it("tek düğümlü zincirde de anlamlı", () => {
      render(<ChainGraph nodes={[dugum("C", 0)]} edges={[]} />);
      expect(ad()).toBe("Atıf zinciri, 1 halka. C baslik — C sahibi, yayınlanan.");
    });
  });

  it("düğüme tıklayınca kimliği bildiriliyor", async () => {
    const secildi = vi.fn();
    render(
      <ChainGraph
        nodes={DUZ_ZINCIR.nodes}
        edges={DUZ_ZINCIR.edges}
        onSelect={secildi}
      />,
    );

    await userEvent.click(screen.getByText("2 ADIM GERİDE"));
    expect(secildi).toHaveBeenCalledWith("A");
  });
});
