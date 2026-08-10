/**
 * Sayi bicimlendirmesi.
 *
 * Kural (CLAUDE.md): kullaniciya gorunen her sayida ondalik ayraci
 * virgul, yuzde isareti sayidan once ve bitisik. `pctRaw` bu kurali
 * bes ekranda birden ciğniyordu ("%84.0") ve yalnizca `ShareBar` kendi
 * icinde duzeltiyordu; ayrac artik tek yerde tanimli. Bu dosya, o tek
 * yerin sessizce geri kaymasini engelliyor.
 */
import { describe, expect, it } from "vitest";
import { money, pct, pctRaw, sayi } from "./api";

describe("pctRaw — hazır yüzde değeri", () => {
  it("ondalık ayracı virgül", () => {
    expect(pctRaw(84)).toBe("%84,0");
    expect(pctRaw(0.5)).toBe("%0,5");
  });

  it("yüzde işareti sayıdan önce ve bitişik", () => {
    expect(pctRaw(12)).toMatch(/^%\d/);
  });

  it("basamak sayısı verilebiliyor; sıfır basamakta ayraç hiç çıkmıyor", () => {
    expect(pctRaw(84.26, 2)).toBe("%84,26");
    expect(pctRaw(84.6, 0)).toBe("%85");
  });

  it("tam sayıda da ondalık gösteriliyor", () => {
    expect(pctRaw(100)).toBe("%100,0");
  });
});

describe("pct — oranı yüzdeye çevirir", () => {
  it("0–1 aralığını yüzdeye taşıyor", () => {
    expect(pct(0.84)).toBe("%84,0");
    expect(pct(1)).toBe("%100,0");
    expect(pct(0)).toBe("%0,0");
  });

  it("pctRaw ile aynı biçimi üretiyor", () => {
    expect(pct(0.326, 2)).toBe(pctRaw(32.6, 2));
  });
});

describe("sayi — yüzde olmayan ölçüm değerleri", () => {
  it("güven ve sönümleme virgüllü yazılıyor", () => {
    expect(sayi(0.91)).toBe("0,91");
    expect(sayi(1)).toBe("1,00");
  });

  it("basamak sayısı verilebiliyor", () => {
    expect(sayi(0.6187, 3)).toBe("0,619");
    expect(sayi(0.123456, 4)).toBe("0,1235");
  });

  it("negatif değerde işaret korunuyor", () => {
    expect(sayi(-0.25)).toBe("-0,25");
  });
});

describe("money — Türk lirası", () => {
  it("binlik ayracı nokta, ondalık ayracı virgül, iki basamak", () => {
    // Simgenin yeri Intl/CLDR'ye birakiliyor (Node ve tarayici tr-TR
    // icin onune koyuyor); sabitlenen sey ayraclar ve basamak sayisi.
    expect(money(1200)).toContain("1.200,00");
    expect(money(129.6)).toContain("129,60");
    expect(money(1200)).toContain("₺");
  });
});
