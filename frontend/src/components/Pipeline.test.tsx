/**
 * Kanit listesi — "ham ölçümler" katmanı.
 *
 * `BASLARKEN.md` jüriye şunu söylüyor: *kanıt satırlarına tıklarsan ham
 * ölçümler açılır*. Açılan şey uzun süre backend'in sözlük anahtarları
 * oldu: `INLIER_COUNT`, `VISUAL_COVERAGE`, `ROTATION_DEG`. Projenin
 * açıklanabilirlik iddiasının en dip katmanı İngilizce değişken
 * adlarıyla yazılıydı.
 *
 * Burada sınanan iki şey, ikisi de sessizce bozulabilir:
 *  1) Ölçümler Türkçe adla ve doğru biçimde görünüyor mu (oran yüzde,
 *     ondalık ayracı virgül).
 *  2) Haritada karşılığı **olmayan** bir anahtar kayboluyor mu.
 *     Kaybolmamalı: bu projede bir ölçümü saklamak, çirkin göstermekten
 *     kötüdür.
 */
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { EvidenceList, StageTimeline } from "./Pipeline";
import type { EvidenceRow, StageLog } from "../api";

/** Geometri aşamasının gerçek çıktısı (backend `geometry.as_evidence`). */
const GEOMETRI: EvidenceRow = {
  stage: "geometry",
  label: "Geometrik doğrulama ve alan ölçümü",
  found: true,
  aciklama: "Kaynak, türev içerikte 631 noktada geometrik olarak eşleşti.",
  detay: {
    good_matches: 812,
    inlier_count: 631,
    inlier_ratio: 0.7771,
    geometric_coverage: 0.9012,
    visual_coverage: 0.8291,
    source_usage: 1.0,
    scale: 0.6304,
    rotation_deg: -0.12,
    mirrored: false,
  },
};

const PHASH: EvidenceRow = {
  stage: "phash",
  label: "Görüntü parmak izi",
  found: true,
  aciklama: "'tam' bölgesinin görüntü parmak izi kaynakla örtüşüyor.",
  detay: { region: "tam", hamming: 6, esik: 12 },
};

async function olcumleriAc(isim: RegExp) {
  const dugme = await screen.findByRole("button", { name: isim });
  await userEvent.click(dugme);
  return dugme.closest("li")!;
}

describe("EvidenceList — ham ölçümler", () => {
  it("geometri ölçümlerini Türkçe adla gösteriyor", async () => {
    render(<EvidenceList rows={[GEOMETRI]} />);
    const satir = await olcumleriAc(/Geometrik doğrulama/);

    expect(within(satir).getByText("Doğrulanan nokta")).toBeInTheDocument();
    expect(within(satir).getByText("631")).toBeInTheDocument();
    expect(
      within(satir).getByText("İçerikte kullanılan alan"),
    ).toBeInTheDocument();
    // İngilizce anahtar hiçbir yerde görünmemeli.
    expect(within(satir).queryByText(/inlier_count/i)).not.toBeInTheDocument();
    expect(
      within(satir).queryByText(/visual_coverage/i),
    ).not.toBeInTheDocument();
  });

  it("oranları yüzdeye, ondalıkları virgüle çeviriyor", async () => {
    render(<EvidenceList rows={[GEOMETRI]} />);
    const satir = await olcumleriAc(/Geometrik doğrulama/);

    // 0,8291 -> %82,9 (pay hesabına giren sayı)
    expect(within(satir).getByText("%82,9")).toBeInTheDocument();
    // 1,0 -> %100,0
    expect(within(satir).getByText("%100,0")).toBeInTheDocument();
    // Ölçek ve dönme oran değil; birimleriyle birlikte
    expect(within(satir).getByText("0,63×")).toBeInTheDocument();
    expect(within(satir).getByText("-0,12°")).toBeInTheDocument();
    expect(within(satir).getByText("hayır")).toBeInTheDocument();
  });

  it("eşik ve uzaklığı birimiyle yazıyor", async () => {
    render(<EvidenceList rows={[PHASH]} />);
    const satir = await olcumleriAc(/Görüntü parmak izi/);

    expect(within(satir).getByText("Fark biti sayısı")).toBeInTheDocument();
    expect(within(satir).getByText("6 bit")).toBeInTheDocument();
    expect(within(satir).getByText("12 bit")).toBeInTheDocument();
  });

  it("itiraz sonrası yeniden ölçümü işaretliyor", async () => {
    // `services/ingest.remeasure` bu bayrağı ekliyor. İlk envanterde
    // atlanmıştı ve ekranda "REMEASURED evet" diye göründü.
    const yeniden: EvidenceRow = {
      ...GEOMETRI,
      aciklama: "İtiraz üzerine SIFT ile yeniden ölçüldü.",
      detay: { ...GEOMETRI.detay, remeasured: true },
    };
    render(<EvidenceList rows={[yeniden]} />);
    const satir = await olcumleriAc(/Geometrik doğrulama/);

    expect(
      within(satir).getByText("İtiraz üzerine yeniden ölçüldü"),
    ).toBeInTheDocument();
    expect(within(satir).queryByText(/remeasured/i)).not.toBeInTheDocument();
  });

  it("tanımsız anahtarı gizlemiyor, ham hâliyle gösteriyor", async () => {
    const yeni: EvidenceRow = {
      ...GEOMETRI,
      detay: { inlier_count: 631, yeni_olcum_2027: 0.42 },
    };
    render(<EvidenceList rows={[yeni]} />);
    const satir = await olcumleriAc(/Geometrik doğrulama/);

    expect(within(satir).getByText("yeni_olcum_2027")).toBeInTheDocument();
    // Tanımsız anahtar eski yedek biçimlendiriciden geçiyor: dört
    // basamak, ondalık ayracı yine virgül.
    expect(within(satir).getByText("0,4200")).toBeInTheDocument();
  });

  it("başlığı backend'in verdiği etiketten alıyor", () => {
    // Arayüz ikinci bir aşama tablosu tutmuyor; tutulduğunda kopyası
    // eksik kalmıştı ve Kaynak Bul ekranında düpedüz "phash_blok"
    // yazıyordu.
    render(
      <EvidenceList
        rows={[
          {
            stage: "phash_blok",
            label: "Blok bazlı görüntü parmak izi",
            found: true,
            aciklama: "",
            detay: { hamming: 4 },
          },
        ]}
      />,
    );
    expect(
      screen.getByText("Blok bazlı görüntü parmak izi"),
    ).toBeInTheDocument();
    expect(screen.queryByText("phash_blok")).not.toBeInTheDocument();
  });

  it("ölçümü olmayan satırda açılır panel yok", () => {
    render(
      <EvidenceList
        rows={[
          {
            stage: "declared",
            label: "Üretici beyanı",
            found: true,
            aciklama: "Üretici remix stüdyosunda bu kaynağı seçti.",
            detay: {},
          },
        ]}
      />,
    );
    expect(screen.queryByText("ölçümler")).not.toBeInTheDocument();
  });
});

/**
 * StageTimeline - Kaynak Bul ekranindaki asama zaman cizelgesi.
 *
 * Bulgu B5 (Gorev 5, K1): "Üstteki eşleşmeyi buldu ama kanıt satırlarını
 * sonuç sandı." `sonucOzeti` bu yuzden var - asama listesinden once,
 * duz Turkce, kac kaynak bulundugunu soyleyen tek cumle.
 */
const STAGES: StageLog[] = [
  { stage: "c2pa", found: false, detail: "", aciklama: "" },
  { stage: "phash", found: true, detail: "1 isabet", aciklama: "" },
];

describe("StageTimeline", () => {
  it("sonucOzeti verilmezse ozet kutusu gorunmuyor", () => {
    render(<StageTimeline stages={STAGES} />);
    expect(screen.queryByText(/^Sonuç:/)).not.toBeInTheDocument();
  });

  it("sonucOzeti asama listesinden once, ayrı bir kutuda goruniyor", () => {
    render(
      <StageTimeline stages={STAGES} sonucOzeti="Sonuç: 2 kaynak bulundu." />,
    );
    expect(screen.getByText("Sonuç: 2 kaynak bulundu.")).toBeInTheDocument();
  });

  it("phash asamasi 'algısal' degil 'görüntü parmak izi' diyor (bulgu B5)", () => {
    render(<StageTimeline stages={STAGES} />);
    expect(screen.getByText("Görüntü parmak izi")).toBeInTheDocument();
    expect(screen.queryByText(/algısal/i)).not.toBeInTheDocument();
  });
});
