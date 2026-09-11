/**
 * Akis ekrani.
 *
 * Asil koruma, 10 Agustos'taki sadelestirmenin geri gelmemesi: her
 * kartta tam genislikte tekrarlanan bir CTA butonu vardi ve gorsel,
 * baslik, buton ucu de ayni yere gidiyordu. Uc tiklama hedefi tek
 * hedef icin - ekran "sablondan uretilmis" gorunuyordu. Kart artik
 * tek bir Emek Karti hedefi gosteriyor; gorselin baglantisi erisim
 * agacinda ve sekme sirasinda yok.
 */
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Feed from "./Feed";
import { api } from "../api";
import { icerik } from "../test/veri";
import { kur, oturumKur } from "../test/kur";

const AKIS = [
  icerik({ id: "c-1", title: "Sabah ışığı", revenue: 1200, derivative_count: 2 }),
  icerik({
    id: "c-2",
    title: "Kırpılmış kare",
    revenue: 0,
    source_count: 1,
    derivative_count: 0,
    remix_allowed: false,
  }),
];

function ekranaGetir(items = AKIS) {
  oturumKur();
  vi.spyOn(api, "feed").mockResolvedValue(items);
  return kur(<Feed />);
}

/** Basligindan yola cikarak kartin kendisini bulur. */
async function kart(baslik: string) {
  const link = await screen.findByRole("link", { name: baslik });
  return link.closest("article")!;
}

beforeEach(() => localStorage.clear());

describe("Feed", () => {
  it("kartta tek bir Emek Kartı hedefi var", async () => {
    ekranaGetir();
    const k = await kart("Sabah ışığı");

    // Tekrarlanan tam genislikte CTA butonu geri gelmesin.
    expect(k.querySelectorAll("button")).toHaveLength(0);
    expect(
      within(k).getAllByRole("link", { name: /Emek Kartı/ }),
    ).toHaveLength(1);
  });

  it("görselin bağlantısı erişim ağacında yok — başlıkla aynı yere gidiyor", async () => {
    ekranaGetir();
    const k = await kart("Sabah ışığı");

    const hedefler = within(k)
      .getAllByRole("link")
      .map((a) => a.getAttribute("href"));
    // Erisilebilir baglantilar: baslik + "Emek Karti" + "Remixle".
    expect(hedefler).toEqual(["/icerik/c-1", "/icerik/c-1", "/remix/c-1"]);

    // Gorsel de ayni yere gidiyor ama ekran okuyucuya ve sekmeye kapali.
    const gorselBagi = k.querySelector("a[aria-hidden='true']")!;
    expect(gorselBagi).toHaveAttribute("href", "/icerik/c-1");
    expect(gorselBagi).toHaveAttribute("tabindex", "-1");
  });

  it("kökeni tek satır düz metinle söylüyor, rozet yığınıyla değil", async () => {
    ekranaGetir();

    expect(
      within(await kart("Sabah ışığı")).getByText("özgün içerik · 2 türev üretildi"),
    ).toBeInTheDocument();
    expect(
      within(await kart("Kırpılmış kare")).getByText("1 kaynaktan türedi"),
    ).toBeInTheDocument();
  });

  it("geliri olmayan kartta tutar yazmıyor", async () => {
    ekranaGetir();

    expect(within(await kart("Sabah ışığı")).getByText(/1\.200,00/)).toBeVisible();
    expect(
      within(await kart("Kırpılmış kare")).queryByText(/₺/),
    ).not.toBeInTheDocument();
  });

  it("remix kapalıysa bağlantı yerine durum yazıyor", async () => {
    ekranaGetir();
    const k = await kart("Kırpılmış kare");

    expect(within(k).getByText("remix kapalı")).toBeInTheDocument();
    expect(
      within(k).queryByRole("link", { name: "Remixle" }),
    ).not.toBeInTheDocument();
  });

  it("akışın başında Kaynak Bul'a giden sabit bir giriş var (bulgu B1)", async () => {
    ekranaGetir();

    const giris = await screen.findByRole("link", {
      name: /Elindeki bir görselin kaynağını mı arıyorsunuz/,
    });
    expect(giris).toHaveAttribute("href", "/kaynak-bul");
  });

  it("akış boşken demo verisini kurma komutunu gösteriyor", async () => {
    ekranaGetir([]);

    expect(
      await screen.findByText("python scripts/seed_demo.py --reset"),
    ).toBeInTheDocument();
  });

  it("uç hata verirse mesaj gösteriliyor", async () => {
    oturumKur();
    vi.spyOn(api, "feed").mockRejectedValue(new Error("Sunucuya ulaşılamadı"));
    kur(<Feed />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Sunucuya ulaşılamadı",
    );
  });

  it("yükleme paneli açılıp kapanıyor", async () => {
    ekranaGetir();
    await kart("Sabah ışığı");

    await userEvent.click(screen.getByRole("button", { name: "İçerik yükle" }));
    expect(
      screen.getByRole("button", { name: "Yüklenecek görseli seç" }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Kapat" }));
    expect(
      screen.queryByRole("button", { name: "Yüklenecek görseli seç" }),
    ).not.toBeInTheDocument();
  });
});
