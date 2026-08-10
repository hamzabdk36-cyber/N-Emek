/**
 * Paylasilan ilkeller.
 *
 * Agirlik `ShareBar`'da: serit bilgiyi yalnizca renk ve genislikle
 * tasiyor, dolayisiyla gorsel olmayan kullanicinin dagilimi
 * ogrenebilecegi tek yer `aria-label`. Bir "sadelestirme" sirasinda o
 * etiketin kisalmasi sessiz bir erisilebilirlik gerilemesi olur;
 * ekranda hicbir sey degismedigi icin de fark edilmez.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfidenceBadge, ShareBar, roleColor } from "./ui";

const SERITLER = [
  { label: "Ceyda Arslan", value: 0.6, color: "#b47ae0" },
  { label: "Burak Demir", value: 0.28, color: "#3fbf7f" },
  { label: "Ayşe Yıldız", value: 0.12, color: "#5b8def" },
];

describe("ShareBar", () => {
  it("dağılımın tamamını metne çeviriyor", () => {
    render(<ShareBar segments={SERITLER} />);

    expect(screen.getByRole("img")).toHaveAccessibleName(
      "Pay dağılımı: Ceyda Arslan %60,0 · Burak Demir %28,0 · Ayşe Yıldız %12,0",
    );
  });

  it("etiket her payı ismiyle sayıyor", () => {
    render(<ShareBar segments={SERITLER} />);
    const etiket = screen.getByRole("img").getAttribute("aria-label") ?? "";

    for (const s of SERITLER) {
      expect(etiket).toContain(s.label);
    }
  });

  it("yüzdeler Türkçe biçimde: ondalık ayracı virgül", () => {
    render(<ShareBar segments={[{ label: "Tek", value: 1, color: "#fff" }]} />);

    expect(screen.getByRole("img")).toHaveAccessibleName(
      "Pay dağılımı: Tek %100,0",
    );
  });

  it("paylar toplamına göre normalleniyor, mutlak değere göre değil", () => {
    // Toplam 1.0 degil: serit yine de dogru orani gostermeli.
    render(
      <ShareBar
        segments={[
          { label: "A", value: 3, color: "#111" },
          { label: "B", value: 1, color: "#222" },
        ]}
      />,
    );

    expect(screen.getByRole("img")).toHaveAccessibleName(
      "Pay dağılımı: A %75,0 · B %25,0",
    );
  });

  it("tüm paylar sıfırken sıfıra bölmüyor", () => {
    render(
      <ShareBar
        segments={[
          { label: "A", value: 0, color: "#111" },
          { label: "B", value: 0, color: "#222" },
        ]}
      />,
    );

    expect(screen.getByRole("img")).toHaveAccessibleName(
      "Pay dağılımı: A %0,0 · B %0,0",
    );
  });
});

describe("ConfidenceBadge", () => {
  it.each([
    ["yuksek", "Yüksek güven"],
    ["orta", "Orta güven"],
    ["dusuk", "Düşük güven"],
  ] as const)("%s bandı '%s' yazıyor", (level, metin) => {
    render(
      <ConfidenceBadge band={{ level, score: 0.91, note: "ölçüldü" }} />,
    );

    expect(screen.getByText(metin)).toBeInTheDocument();
    expect(screen.getByText("0.91")).toBeInTheDocument();
  });
});

describe("roleColor", () => {
  it("üretici altın, platform nötr — tema anlam renkleriyle çakışmıyor", () => {
    expect(roleColor("creator")).toBe("#f2b134");
    expect(roleColor("platform")).toBe("#3a4250");
  });

  it("kaynak paleti sırayla dağıtılıyor ve başa dönüyor", () => {
    const ilk = roleColor("source", 0);
    expect(roleColor("source", 1)).not.toBe(ilk);
    expect(roleColor("source", 5)).toBe(ilk);
  });
});
