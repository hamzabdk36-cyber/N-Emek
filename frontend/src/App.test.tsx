/**
 * Ust cubuk: rol rozeti.
 *
 * Iki uc moderator yetkisi istiyor (kampanya havuzunu dagitmak, itirazi
 * karara baglamak) ve rol gorunmezken 403 alan kisi sebebini
 * anlamiyordu. Rozet gorunur olsun diye eklendi; gorunmez oldugunda da
 * sessizce kaybolabilecegi icin testi var.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { render } from "@testing-library/react";
import App from "./App";
import { api } from "./api";
import { KULLANICILAR, oturumKur } from "./test/kur";

function kurUygulama() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );
}

describe("Üst çubuk rol rozeti", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
    // Akis ekrani da yukleniyor; bos liste yeterli.
    vi.spyOn(api, "feed").mockResolvedValue([]);
  });

  it("moderatör olmayan kullanıcıda rozet yok", async () => {
    oturumKur("u-ayse");
    kurUygulama();

    await screen.findByDisplayValue("Ayşe Yıldız");
    expect(screen.queryByText("moderatör")).toBeNull();
  });

  it("moderatör rolündeki kullanıcıda rozet görünüyor", async () => {
    oturumKur("u-ceyda");
    kurUygulama();

    expect(await screen.findByText("moderatör")).toBeInTheDocument();
  });

  it("kullanıcı değişince rozet de değişiyor", async () => {
    oturumKur("u-ayse");
    kurUygulama();

    const secici = await screen.findByDisplayValue("Ayşe Yıldız");
    expect(screen.queryByText("moderatör")).toBeNull();

    const ceyda = KULLANICILAR.find((u) => u.handle === "ceyda")!;
    await userEvent.selectOptions(secici, ceyda.id);

    await waitFor(() =>
      expect(screen.getByText("moderatör")).toBeInTheDocument(),
    );
  });
});
