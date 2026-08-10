/**
 * Hata siniri.
 *
 * Sinanan sey su: bir bilesen patladiginda ekranda beyaz sayfa degil,
 * Turkce bir aciklama ve cikis yolu kaliyor. Bu, jurinin gorecegi en
 * kotu senaryonun karsiligi - ve dogasi geregi elle denenmesi zor bir
 * yol, cunku hatayi bilerek uretmek gerekiyor.
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { HataSiniri } from "./HataSiniri";

/** Bayrak acikken patlayan bilesen; "yeniden dene" boylece sinanabiliyor. */
let patla = true;
function Patlayan() {
  if (patla) throw new Error("kapsama hesabı çöktü");
  return <p>Ekran çizildi</p>;
}

beforeEach(() => {
  patla = true;
  // React yakalanan hatayi yine de konsola basiyor; test ciktisini
  // kirletmesin.
  vi.spyOn(console, "error").mockImplementation(() => {});
});

describe("HataSiniri", () => {
  it("hata yokken çocuklarını olduğu gibi çiziyor", () => {
    render(
      <HataSiniri>
        <p>Normal içerik</p>
      </HataSiniri>,
    );

    expect(screen.getByText("Normal içerik")).toBeInTheDocument();
  });

  it("çocuk patlayınca beyaz ekran yerine Türkçe açıklama gösteriyor", () => {
    render(
      <HataSiniri>
        <Patlayan />
      </HataSiniri>,
    );

    expect(screen.getByText("Bu ekran açılamadı")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent(
      /Beklenmedik bir sorun oluştu/,
    );
    // Cikis yolu var: hem yeniden deneme hem yenileme.
    expect(
      screen.getByRole("button", { name: "Yeniden dene" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Sayfayı yenile" }),
    ).toBeInTheDocument();
  });

  it("yığın izi ekrana dökülmüyor, ayrıntı kapalı duruyor", () => {
    render(
      <HataSiniri>
        <Patlayan />
      </HataSiniri>,
    );

    const ayrinti = screen.getByText("Teknik ayrıntı").closest("details")!;
    expect(ayrinti).not.toHaveAttribute("open");
    // Mesaj ayrintinin icinde; acilinca gorulebiliyor.
    expect(ayrinti).toHaveTextContent("kapsama hesabı çöktü");
  });

  it("hatayı konsola bırakıyor — demoda sebebi kaybolmasın", () => {
    render(
      <HataSiniri>
        <Patlayan />
      </HataSiniri>,
    );

    expect(console.error).toHaveBeenCalledWith(
      "Arayuzde yakalanmis hata:",
      expect.objectContaining({ message: "kapsama hesabı çöktü" }),
      expect.any(String),
    );
  });

  it("'Yeniden dene' sınırı sıfırlıyor", async () => {
    render(
      <HataSiniri>
        <Patlayan />
      </HataSiniri>,
    );
    expect(screen.getByText("Bu ekran açılamadı")).toBeInTheDocument();

    patla = false;
    await userEvent.click(screen.getByRole("button", { name: "Yeniden dene" }));

    expect(screen.getByText("Ekran çizildi")).toBeInTheDocument();
    expect(screen.queryByText("Bu ekran açılamadı")).not.toBeInTheDocument();
  });

  it("hata sınırın dışına taşmıyor — kardeş içerik ayakta kalıyor", () => {
    render(
      <div>
        <nav>Gezinme</nav>
        <HataSiniri>
          <Patlayan />
        </HataSiniri>
      </div>,
    );

    // Gezinme duruyor: kullanici baska bir ekrana gecebilir.
    expect(screen.getByText("Gezinme")).toBeInTheDocument();
    expect(screen.getByText("Bu ekran açılamadı")).toBeInTheDocument();
  });
});
