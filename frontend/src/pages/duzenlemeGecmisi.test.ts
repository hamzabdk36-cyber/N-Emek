/**
 * Geri alma yiginin degismezleri.
 *
 * Asil iddia: **geri alma son cizim ya da yazi islemini butun halinde
 * kaldirir ve yalnizca onu kaldirir.** Studyonun kendisi jsdom'da
 * calismiyor (canvas baglami yok), bu yuzden davranisin sinanabildigi
 * tek yer burasi.
 */
import { describe, expect, it } from "vitest";
import {
  GECMIS_SINIRI,
  gecmiseYaz,
  gecmistenAl,
  type DuzenlemeDurumu,
  type Stroke,
  type TextLayer,
} from "./duzenlemeGecmisi";

const cizgi = (renk = "#f2b134"): Stroke => ({
  points: [
    { x: 10, y: 10 },
    { x: 20, y: 24 },
  ],
  color: renk,
  width: 8,
});

const yazi = (metin: string): TextLayer => ({
  x: 40,
  y: 60,
  text: metin,
  size: 32,
  color: "#ffffff",
});

const bos: DuzenlemeDurumu = { strokes: [], texts: [] };

describe("gecmistenAl", () => {
  it("boş yığında geri alınacak bir şey yok", () => {
    const { gecmis, durum } = gecmistenAl([]);
    expect(durum).toBeNull();
    expect(gecmis).toEqual([]);
  });

  it("son yazılan durumu aynen geri veriyor", () => {
    const oncesi: DuzenlemeDurumu = { strokes: [cizgi()], texts: [yazi("A")] };
    const yigin = gecmiseYaz([], oncesi);

    const { durum } = gecmistenAl(yigin);
    expect(durum).toEqual(oncesi);
  });

  it("iki kez geri almak iki işlem geriye gidiyor", () => {
    // Bos tuval -> bir cizgi -> iki cizgi. Her islem oncesi yigina yaziliyor.
    const birCizgi: DuzenlemeDurumu = { strokes: [cizgi()], texts: [] };

    let yigin = gecmiseYaz([], bos);
    yigin = gecmiseYaz(yigin, birCizgi);

    const ilk = gecmistenAl(yigin);
    expect(ilk.durum).toEqual(birCizgi);

    const ikinci = gecmistenAl(ilk.gecmis);
    expect(ikinci.durum).toEqual(bos);
    expect(ikinci.gecmis).toEqual([]);
  });

  it("yığından çıkarılan adım yığında kalmıyor", () => {
    const yigin = gecmiseYaz(gecmiseYaz([], bos), {
      strokes: [cizgi()],
      texts: [],
    });
    expect(yigin).toHaveLength(2);
    expect(gecmistenAl(yigin).gecmis).toHaveLength(1);
  });
});

describe("gecmiseYaz", () => {
  it("kopya alıyor: sonradan diziye eklemek geçmişi bozmuyor", () => {
    // Kritik: yigin canli diziyi referansla tutsaydi, bir sonraki firca
    // darbesi gecmisteki adimi da degistirir ve geri alma hicbir sey
    // yapmamis gibi gorunurdu.
    const cizgiler: Stroke[] = [cizgi()];
    const yigin = gecmiseYaz([], { strokes: cizgiler, texts: [] });

    cizgiler.push(cizgi("#ff0000"));

    expect(gecmistenAl(yigin).durum!.strokes).toHaveLength(1);
  });

  it("sınıra ulaşınca en eski adım düşüyor, yığın büyümüyor", () => {
    let yigin: DuzenlemeDurumu[] = [];
    for (let i = 0; i < GECMIS_SINIRI + 5; i++) {
      yigin = gecmiseYaz(yigin, { strokes: [], texts: [yazi(`adım ${i}`)] });
    }

    expect(yigin).toHaveLength(GECMIS_SINIRI);
    // En eskiler dustu: kalan en alttaki adim 5 numarali olan.
    expect(yigin[0].texts[0].text).toBe("adım 5");
    expect(yigin[yigin.length - 1].texts[0].text).toBe(
      `adım ${GECMIS_SINIRI + 4}`,
    );
  });

  it("sınır çağrı başına verilebiliyor", () => {
    let yigin: DuzenlemeDurumu[] = [];
    for (let i = 0; i < 6; i++) {
      yigin = gecmiseYaz(yigin, { strokes: [], texts: [yazi(`${i}`)] }, 3);
    }
    expect(yigin).toHaveLength(3);
    expect(yigin[0].texts[0].text).toBe("3");
  });
});

describe("kapsam", () => {
  it("geçmiş yalnızca çizim ve yazı taşıyor — kırpma ve filtre dışarıda", () => {
    // Bu bilincli bir sinir: kirpmanin kendi "Vazgec"i, filtrenin
    // "Filtresiz" secenegi var. Yigin sadece geri donusu olmayan iki
    // katman icin duruyor. Durum nesnesine yeni bir alan eklenirse bu
    // test kirmiziya doner ve karar yeniden dusunulur.
    const { durum } = gecmistenAl(gecmiseYaz([], bos));
    expect(Object.keys(durum!).sort()).toEqual(["strokes", "texts"]);
  });
});
