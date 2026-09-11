/**
 * Kaynak/turev karsilastirmasi ve eslesen bolge maskesi.
 *
 * Canvas'a piksel birlestirme jsdom'da calismiyor (gercek `getContext`
 * yok, `Image` da agdan hic yuklenmiyor) - bu yuzden testler, maske
 * cizilmeden *once* de dogru olmasi gereken seyleri sinar: lejant,
 * baslik metni ve onay kutusu etiketi, `ready` durumuna bakmadan
 * `maskUrl` var olur olmaz DOM'da beliriyor.
 *
 * Bulgu B3 (KULLANILABILIRLIK-SONUCLARI.md): iki katilimci parlak
 * alani "degistirilen bolge" sandi - tam tersi. Duzeltme sonrasi
 * lejant iki ornegi aciktan yaziyor ve kaynagin adini soyluyor.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ImageCompare } from "./ImageCompare";

const TEMEL = {
  sourceUrl: "/api/contents/kaynak/image",
  derivativeUrl: "/api/contents/turev/image",
  sourceLabel: "Ayşe Yılmaz",
  derivativeLabel: "Bulduğum kare",
};

describe("ImageCompare", () => {
  it("maske yoksa lejant ve onay kutusu hiç görünmüyor", () => {
    render(<ImageCompare {...TEMEL} maskUrl={null} />);

    expect(screen.queryByText(/gelen piksel/)).not.toBeInTheDocument();
    expect(
      screen.queryByRole("checkbox", { name: /Kaynaktan gelen bölgeyi vurgula/ }),
    ).not.toBeInTheDocument();
    expect(screen.getByText("türev içerik")).toBeInTheDocument();
  });

  it("maske varsa lejant kaynağın adını söylüyor, rengi değil (bulgu B3)", () => {
    render(<ImageCompare {...TEMEL} maskUrl="/api/masks/e-1" coverage={0.412} />);

    expect(
      screen.getByText("parlak: Ayşe Yılmaz'dan gelen piksel"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("gri: Bulduğum kare üreticisinin eklediği"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: "Kaynaktan gelen bölgeyi vurgula" }),
    ).toBeChecked();
  });

  it("başlık, parlak alanın hangi kaynaktan geldiğini söylüyor — 'eşleşen bölge' değil", () => {
    render(<ImageCompare {...TEMEL} maskUrl="/api/masks/e-1" />);

    expect(
      screen.getByText("parlak alan: Ayşe Yılmaz'dan geldiği ölçümle doğrulanan bölge"),
    ).toBeInTheDocument();
  });

  it("onay kutusu kapatılınca lejant ve vurgu başlığı kayboluyor", async () => {
    render(<ImageCompare {...TEMEL} maskUrl="/api/masks/e-1" />);

    await userEvent.click(
      screen.getByRole("checkbox", { name: "Kaynaktan gelen bölgeyi vurgula" }),
    );

    expect(screen.queryByText(/gelen piksel/)).not.toBeInTheDocument();
    expect(screen.getByText("türev içerik")).toBeInTheDocument();
  });

  it("ölçülen alan oranı gösteriliyor", () => {
    render(<ImageCompare {...TEMEL} maskUrl="/api/masks/e-1" coverage={0.412} />);

    expect(screen.getByText("%41,2")).toBeInTheDocument();
  });
});
