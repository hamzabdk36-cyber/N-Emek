/**
 * Oturum saglayicisi.
 *
 * Arayuzde gorunur bir degisiklik yok - secici ayni secici - ama artik
 * secim yapmak oturum acmak demek. Gorunmez oldugu icin de sessizce
 * bozulabilir: jeton alinmazsa yalnizca *mutasyon* uclari 401 doner,
 * akis ve Emek Karti normal gorunmeye devam eder.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";
import { SessionProvider, useSession } from "./session";
import { render } from "@testing-library/react";
import { KULLANICILAR, oturumKur } from "./test/kur";

function Sonda() {
  const { currentUser, users, loading } = useSession();
  if (loading) return <p>yükleniyor</p>;
  return (
    <div>
      <p>aktif: {currentUser?.display_name ?? "yok"}</p>
      <p>kullanıcı sayısı: {users.length}</p>
      {users.map((u) => (
        <button key={u.id} onClick={() => useSecici(u.id)}>
          {u.display_name}
        </button>
      ))}
    </div>
  );
}

// Secici, bilesen icinden cagrilabilsin diye ayri: `useSession` bir
// kanca oldugu icin olay isleyicisinin icinde cagrilamaz.
let useSecici: (id: string) => void = () => {};

function Kabuk() {
  return (
    <SessionProvider>
      <Degistirici />
      <Sonda />
    </SessionProvider>
  );
}

function Degistirici() {
  const { users, setCurrentUser } = useSession();
  useSecici = (id: string) => {
    const hedef = users.find((u) => u.id === id);
    if (hedef) setCurrentUser(hedef);
  };
  return null;
}

beforeEach(() => localStorage.clear());

describe("SessionProvider", () => {
  it("açılışta kayıtlı kullanıcı için oturum açıyor", async () => {
    oturumKur("u-burak");
    render(<Kabuk />);

    expect(await screen.findByText("aktif: Burak Demir")).toBeInTheDocument();
    expect(api.oturum).toHaveBeenCalledWith("u-burak");
  });

  it("kayıt yoksa listedeki ilk kullanıcıyla oturum açıyor", async () => {
    oturumKur();
    localStorage.clear();
    render(<Kabuk />);

    expect(await screen.findByText("aktif: Ayşe Yıldız")).toBeInTheDocument();
    expect(api.oturum).toHaveBeenCalledWith(KULLANICILAR[0].id);
  });

  it("kullanıcı değişince yeni jeton alınıyor ve seçim saklanıyor", async () => {
    oturumKur("u-ayse");
    render(<Kabuk />);
    await screen.findByText("aktif: Ayşe Yıldız");

    await userEvent.click(screen.getByRole("button", { name: "Ceyda Arslan" }));

    await waitFor(() =>
      expect(api.oturum).toHaveBeenCalledWith("u-ceyda"),
    );
    expect(localStorage.getItem("nemek.actor")).toBe("u-ceyda");
    expect(await screen.findByText("aktif: Ceyda Arslan")).toBeInTheDocument();
  });

  it("backend kapalıysa çökmüyor, oturum boş kalıyor", async () => {
    vi.spyOn(api, "users").mockRejectedValue(new Error("Sunucuya ulaşılamadı"));
    vi.spyOn(api, "health").mockResolvedValue({
      status: "ok",
      indexed_contents: 0,
      device: "cpu",
      c2pa_signing: false,
    });
    const oturum = vi.spyOn(api, "oturum");

    render(<Kabuk />);

    expect(await screen.findByText("aktif: yok")).toBeInTheDocument();
    expect(screen.getByText("kullanıcı sayısı: 0")).toBeInTheDocument();
    expect(oturum).not.toHaveBeenCalled();
  });

  it("oturum açma ucu hata verirse arayüz yine çiziliyor", async () => {
    oturumKur("u-ayse");
    vi.spyOn(api, "oturum").mockRejectedValue(new Error("oturum açılamadı"));

    render(<Kabuk />);

    // Kullanici listesi geldi, yalnizca jeton yok: ekran ayakta kalmali.
    expect(await screen.findByText("kullanıcı sayısı: 3")).toBeInTheDocument();
  });
});
