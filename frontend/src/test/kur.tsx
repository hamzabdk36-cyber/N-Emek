/**
 * Sayfa testleri icin ortak kurulum.
 *
 * Sayfalar iki baglamdan besleniyor: yonlendirici (`useParams`) ve
 * oturum (`useSession`). Ikisini de her testte elle sarmalamak yerine
 * tek yerden veriliyor ki bir baglam eklendiginde testler tek dosyada
 * guncellensin.
 */
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { api, type Health, type User } from "../api";
import { SessionProvider } from "../session";
import { kullanici } from "./veri";
import { vi } from "vitest";

export const KULLANICILAR: User[] = [
  kullanici({ id: "u-ayse", handle: "ayse", display_name: "Ayşe Yıldız" }),
  kullanici({
    id: "u-burak",
    handle: "burak",
    display_name: "Burak Demir",
    accent: "#3fbf7f",
  }),
  // Demo verisindeki gibi: moderator rolu Ceyda'da (scripts/seed_demo.py).
  kullanici({
    id: "u-ceyda",
    handle: "ceyda",
    display_name: "Ceyda Arslan",
    accent: "#b47ae0",
    role: "moderator",
  }),
];

const SAGLIK: Health = {
  status: "ok",
  indexed_contents: 3,
  device: "cpu",
  c2pa_signing: true,
};

/**
 * Oturumun ihtiyac duydugu uclari sahteler ve kimin oturum actigini
 * secer. `SessionProvider` secimi `localStorage`'dan okuyor, sonra
 * `POST /api/oturum` ile jeton aliyor.
 */
export function oturumKur(aktifKullaniciId = KULLANICILAR[0].id) {
  localStorage.setItem("nemek.actor", aktifKullaniciId);
  vi.spyOn(api, "users").mockResolvedValue(KULLANICILAR);
  vi.spyOn(api, "health").mockResolvedValue(SAGLIK);
  vi.spyOn(api, "oturum").mockImplementation(async (userId: string) => ({
    token: `sahte-jeton.${userId}`,
    expires_at: Math.floor(Date.now() / 1000) + 3600,
    user: KULLANICILAR.find((u) => u.id === userId) ?? KULLANICILAR[0],
  }));
}

export function kur(
  ui: ReactElement,
  { yol = "/", desen = "/" }: { yol?: string; desen?: string } = {},
) {
  return render(
    <MemoryRouter initialEntries={[yol]}>
      <SessionProvider>
        <Routes>
          <Route path={desen} element={ui} />
          {/* Akisa yonlendiren ekranlar (ornegin silme sonrasi
              `navigate("/")`) bosluga dusmesin: eslesmeyen rota
              React Router'i konsola uyari yazdiriyor ve testte
              yonlendirmenin gerceklestigi dogrulanamiyordu. */}
          {desen !== "/" && <Route path="/" element={<p>Akış</p>} />}
        </Routes>
      </SessionProvider>
    </MemoryRouter>,
  );
}
