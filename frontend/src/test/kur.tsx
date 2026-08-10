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
  kullanici({
    id: "u-ceyda",
    handle: "ceyda",
    display_name: "Ceyda Arslan",
    accent: "#b47ae0",
  }),
];

const SAGLIK: Health = {
  status: "ok",
  indexed_contents: 3,
  device: "cpu",
  c2pa_signing: true,
};

/**
 * Oturumun ihtiyac duydugu iki ucu sahteler ve kimin oturum actigini
 * secer. `SessionProvider` secimi `localStorage`'dan okuyor.
 */
export function oturumKur(aktifKullaniciId = KULLANICILAR[0].id) {
  localStorage.setItem("nemek.actor", aktifKullaniciId);
  vi.spyOn(api, "users").mockResolvedValue(KULLANICILAR);
  vi.spyOn(api, "health").mockResolvedValue(SAGLIK);
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
        </Routes>
      </SessionProvider>
    </MemoryRouter>,
  );
}
