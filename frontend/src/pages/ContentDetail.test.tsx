/**
 * Emek Karti ekrani - demonun kapak karesi.
 *
 * Iki sey sinaniyor:
 *  1) Bir pay satiri acildiginda payin *gerekcesi* goruluyor mu -
 *     kapsama, guven, sonumleme ve bunlari carpip sonuca goturen
 *     formul satiri. Jurinin "neden bu kadar" sorusunun cevabi bu dort
 *     sayi; biri kaybolursa ekran yine duzgun gorunur ama iddia
 *     bosalir.
 *  2) Itiraz kutusu yalnizca o payin sahibinde cikiyor mu. Su an
 *     yetkilendirme sunucuda yok (Etap A4), dolayisiyla bu kurali
 *     tutan tek yer arayuz.
 */
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ContentDetail from "./ContentDetail";
import { api } from "../api";
import { emekKarti } from "../test/veri";
import { kur, oturumKur } from "../test/kur";

function ekranaGetir(aktif = "u-ayse") {
  oturumKur(aktif);
  vi.spyOn(api, "labourCard").mockResolvedValue(emekKarti());
  return kur(<ContentDetail />, { yol: "/icerik/C", desen: "/icerik/:id" });
}

/**
 * Kart gelene kadar bekler.
 *
 * Baslik metnine gore aranmiyor: ayni baslik zincir grafigindeki
 * yaprak dugumde de yaziyor, dolayisiyla metin tek basina benzersiz
 * degil. Sayfa basligi rolunden aranan tek h1.
 */
function kartYuklendi() {
  return screen.findByRole("heading", { level: 1, name: "Şehir kolajı" });
}

/**
 * Bir tarafin pay satirini acar ve satirin kendisini dondurur.
 *
 * Ilk kaynak satiri artik varsayilan acik geliyor (bulgu B4), yani
 * "acmak" bazen hicbir tiklama gerektirmiyor - onceden kapali oldugunu
 * varsaymiyoruz, once mevcut durumu okuyoruz.
 */
async function payiAc(isim: RegExp) {
  const dugme = await screen.findByRole("button", { name: isim });
  if (dugme.getAttribute("aria-expanded") !== "true") {
    await userEvent.click(dugme);
    await waitFor(() => expect(dugme).toHaveAttribute("aria-expanded", "true"));
  }
  return dugme.closest("li")!;
}

beforeEach(() => localStorage.clear());

describe("ContentDetail — Emek Kartı", () => {
  it("köken anlatısını ve dağıtılan tutarı gösteriyor", async () => {
    ekranaGetir();

    expect(await kartYuklendi()).toBeInTheDocument();
    expect(
      screen.getByText(/köken kanıtlardan yeniden kuruldu/i),
    ).toBeInTheDocument();
    expect(screen.getByText("Köken yeniden kuruldu")).toBeInTheDocument();
    expect(screen.getByText("Dağıtılan")).toBeInTheDocument();
  });

  it("pay dağılımını erişilebilir metne çeviriyor", async () => {
    ekranaGetir();
    await kartYuklendi();

    // Platform payi seritte 0 genislikte, ama etikette yine sayiliyor.
    expect(
      screen.getByRole("img", { name: /^Pay dağılımı:/ }),
    ).toHaveAccessibleName(/Ceyda Arslan .* Burak Demir .* Ayşe Yıldız/);
  });

  it("pay satırı açılınca kapsama, güven, sönümleme ve formül görünüyor", async () => {
    ekranaGetir();
    const satir = await payiAc(/Ayşe Yıldız/);

    for (const etiket of ["kapsama", "güven", "sönümleme", "ham ağırlık"]) {
      expect(within(satir).getByText(etiket)).toBeInTheDocument();
    }
    // Formul satiri: carpanlar ve sonuc birlikte yaziyor. Hepsi Turkce
    // bicimde - ondalik ayraci virgul, yuzde isareti sayidan once.
    expect(
      within(satir).getByText(
        "pay = kapsama %84,0 × güven 0,91 × sönümleme 0,81 = 0,619",
      ),
    ).toBeInTheDocument();
    expect(within(satir).getByText("%84,0")).toBeInTheDocument();
    expect(within(satir).getByText("0,91")).toBeInTheDocument();
    expect(within(satir).getByText(/kaynak tabanı uygulandı/)).toBeInTheDocument();
  });

  it("ilk kaynak satırı varsayılan açık geliyor, diğerleri kapalı kalıyor (bulgu B4)", async () => {
    ekranaGetir();
    await kartYuklendi();

    // Ilk kaynak (Burak, distribution.parties sirasinda ceyda'dan sonraki
    // ilk source) tiklamadan aciliyor: kullanicilarin ucte biri gerekceyi
    // satiri acmayi kesfedemedigi icin bulundu (KULLANILABILIRLIK-SONUCLARI.md).
    const burak = (await screen.findByRole("button", { name: /Burak Demir/ }))
      .closest("li")!;
    expect(within(burak).getByText(/pay = kapsama/)).toBeInTheDocument();

    // Baska bir kaynak (Ayse) acilmadan kapali kalmaya devam ediyor.
    const ayse = screen.getByRole("button", { name: /Ayşe Yıldız/ }).closest("li")!;
    expect(within(ayse).queryByText(/pay = kapsama/)).not.toBeInTheDocument();
  });

  it("itiraz kutusu yalnızca payın sahibine çıkıyor", async () => {
    ekranaGetir("u-ayse");

    const kendi = await payiAc(/Ayşe Yıldız/);
    expect(
      within(kendi).getByRole("button", { name: "Yeniden ölçüm iste" }),
    ).toBeInTheDocument();

    const baskasi = await payiAc(/Burak Demir/);
    expect(
      within(baskasi).queryByRole("button", { name: "Yeniden ölçüm iste" }),
    ).not.toBeInTheDocument();
  });

  it("oturum değişince itiraz hakkı da değişiyor", async () => {
    ekranaGetir("u-burak");

    const burak = await payiAc(/Burak Demir/);
    expect(
      within(burak).getByRole("button", { name: "Yeniden ölçüm iste" }),
    ).toBeInTheDocument();

    const ayse = await payiAc(/Ayşe Yıldız/);
    expect(
      within(ayse).queryByRole("button", { name: "Yeniden ölçüm iste" }),
    ).not.toBeInTheDocument();
  });

  it("üretici ve platform satırlarında itiraz yok", async () => {
    ekranaGetir("u-ceyda");

    const uretici = await payiAc(/Ceyda Arslan/);
    expect(
      within(uretici).queryByRole("button", { name: "Yeniden ölçüm iste" }),
    ).not.toBeInTheDocument();

    const platform = await payiAc(/Platform/);
    expect(
      within(platform).queryByRole("button", { name: "Yeniden ölçüm iste" }),
    ).not.toBeInTheDocument();
  });

  it("itiraz düğmesinin altında kayıt açıldığı yazıyor ve açılınca üç adım listelenir (bulgu B2)", async () => {
    ekranaGetir("u-ayse");
    const satir = await payiAc(/Ayşe Yıldız/);

    expect(
      within(satir).getByText("İtiraz kaydı açılır"),
    ).toBeInTheDocument();

    await userEvent.click(
      within(satir).getByRole("button", { name: "Yeniden ölçüm iste" }),
    );

    expect(within(satir).getByText(/hassas bir dedektörle/)).toBeInTheDocument();
    expect(within(satir).getByText(/tüm dağıtımı güncellenir/)).toBeInTheDocument();
    expect(within(satir).getByText(/insan incelemesine düşer/)).toBeInTheDocument();
  });

  it("itiraz gönderilince bağ yeniden ölçülüyor ve kart tazeleniyor", async () => {
    ekranaGetir("u-ayse");
    const ac = vi
      .spyOn(api, "openDispute")
      .mockResolvedValue({ id: "d-1", status: "open" });
    const coz = vi.spyOn(api, "resolveDispute").mockResolvedValue({
      id: "d-1",
      status: "resolved",
      changed: true,
      summary: "Bağ SIFT ile yeniden ölçüldü; kapsama %84,0 → %91,0 güncellendi.",
      resolution: {},
    });

    const satir = await payiAc(/Ayşe Yıldız/);
    await userEvent.click(
      within(satir).getByRole("button", { name: "Yeniden ölçüm iste" }),
    );
    await userEvent.click(
      within(satir).getByRole("button", { name: "İtirazı gönder" }),
    );

    // İtirazı kimin açtığı gövdede gitmiyor; uç bunu jetondan okuyor.
    expect(ac).toHaveBeenCalledWith("e-ab", expect.any(String));
    expect(coz).toHaveBeenCalledWith("d-1");
    expect(
      await within(satir).findByText(/yeniden ölçüldü/),
    ).toBeInTheDocument();
    // Paylar degismis olabilir; kart yeniden cekiliyor.
    expect(api.labourCard).toHaveBeenCalledTimes(2);
  });

  it("zincir grafiği çiziliyor", async () => {
    ekranaGetir();
    await kartYuklendi();

    // Etiket artik sabit degil: zincirin tamamini anlatiyor. Metnin
    // kendisi ChainGraph.test.tsx'te olculuyor, burada yalnizca
    // grafigin ekrana geldigi ve etiketini kartin verisinden aldigi.
    expect(
      screen.getByRole("img", { name: /^Atıf zinciri, \d+ halka\./ }),
    ).toBeInTheDocument();
    expect(screen.getByText("YAYINLANAN")).toBeInTheDocument();
  });

  it("silme düğmesi yalnızca içeriğin sahibine çıkıyor", async () => {
    // Fiksturde icerigin sahibi Ceyda.
    ekranaGetir("u-ayse");
    await kartYuklendi();
    expect(
      screen.queryByRole("button", { name: "İçeriği sil" }),
    ).not.toBeInTheDocument();
  });

  it("sahibinde silme düğmesi var ve tek tıkla silmiyor", async () => {
    ekranaGetir("u-ceyda");
    const sil = vi.spyOn(api, "deleteContent");
    await kartYuklendi();

    await userEvent.click(screen.getByRole("button", { name: "İçeriği sil" }));

    // Onay adimi: dugme silme cagrisini dogrudan yapmiyor.
    expect(sil).not.toHaveBeenCalled();
    expect(screen.getByText(/kalıcı olarak silinecek/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Evet, sil" })).toBeInTheDocument();
  });

  it("onaylanınca siliniyor", async () => {
    ekranaGetir("u-ceyda");
    const sil = vi.spyOn(api, "deleteContent").mockResolvedValue({
      content_id: "C",
      silinen_bag: 2,
      silinen_itiraz: 0,
      silinen_maske: 2,
      gorsel_silindi: true,
    });
    await kartYuklendi();

    await userEvent.click(screen.getByRole("button", { name: "İçeriği sil" }));
    await userEvent.click(screen.getByRole("button", { name: "Evet, sil" }));

    expect(sil).toHaveBeenCalledWith("C");
    // Icerik artik yok; sayfada kalmak 404 demek olurdu.
    expect(await screen.findByText("Akış")).toBeInTheDocument();
  });

  it("vazgeçilince silme çağrısı yapılmıyor", async () => {
    ekranaGetir("u-ceyda");
    const sil = vi.spyOn(api, "deleteContent");
    await kartYuklendi();

    await userEvent.click(screen.getByRole("button", { name: "İçeriği sil" }));
    await userEvent.click(screen.getByRole("button", { name: "Vazgeç" }));

    expect(sil).not.toHaveBeenCalled();
    expect(
      screen.getByRole("button", { name: "İçeriği sil" }),
    ).toBeInTheDocument();
  });

  it("ödemesi olan içerikte 409 mesajı gösteriliyor", async () => {
    // Uc, 409 govdesindeki `detail` metnini `Error.message` olarak
    // veriyor (bkz. api.ts::req). Juri bu mesaji gorecek: mali kaydin
    // korundugunu anlatan yer burasi.
    ekranaGetir("u-ceyda");
    vi.spyOn(api, "deleteContent").mockRejectedValue(
      new Error(
        "Bu içeriğe 3 ödeme bağlı. Gerçekleşmiş ödemelerin kaydı silinemez; " +
          "mali kayıtların bütünlüğü korunmalıdır.",
      ),
    );
    await kartYuklendi();

    await userEvent.click(screen.getByRole("button", { name: "İçeriği sil" }));
    await userEvent.click(screen.getByRole("button", { name: "Evet, sil" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /Gerçekleşmiş ödemelerin kaydı silinemez/,
    );
    // Onay kapaniyor, icerik duruyor.
    expect(
      screen.getByRole("button", { name: "İçeriği sil" }),
    ).toBeInTheDocument();
  });

  it("uç hata verirse mesaj gösteriliyor", async () => {
    oturumKur();
    vi.spyOn(api, "labourCard").mockRejectedValue(new Error("İçerik bulunamadı"));
    kur(<ContentDetail />, { yol: "/icerik/yok", desen: "/icerik/:id" });

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "İçerik bulunamadı",
    );
  });
});
