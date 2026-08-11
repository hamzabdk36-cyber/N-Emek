/**
 * Remix Studyosu'nun geri alma yigini - saf fonksiyonlar.
 *
 * Neden bilesenden ayri
 * ---------------------
 * jsdom'da canvas baglami yok; studyonun tamami ucuza test edilemiyor.
 * Yigin mantigi DOM'dan bagimsiz oldugunda "geri al yalnizca son
 * katmani siler, kirpma ve filtre yerinde kalir" iddiasi dogrudan
 * sinanabiliyor (`duzenlemeGecmisi.test.ts`). Ayni gerekce
 * `components/chainLayout.ts` icin de gecerliydi.
 *
 * Kapsam bilincli olarak dar: **yalnizca cizim ve yazi katmanlari**.
 * Kirpma ve filtre geri alinmaz, cunku ikisi de tek bir degerdir ve
 * kendi arayuzlerinden zaten degistirilebiliyor (kirpma icin "Vazgec",
 * filtre icin "Filtresiz"). Yanlis bir firca darbesinin ise tek caresi
 * "Tumunu sifirla" idi - kirpma, yazi, filtre dahil her sey giderdi.
 * Yigin tam o bosluk icin var.
 */

export interface TextLayer {
  x: number;
  y: number;
  text: string;
  size: number;
  color: string;
}

export interface Stroke {
  points: { x: number; y: number }[];
  color: string;
  width: number;
}

/** Geri alinabilir olanin tamami: cizimler ve yazilar. */
export interface DuzenlemeDurumu {
  strokes: Stroke[];
  texts: TextLayer[];
}

/**
 * Kac adim geriye gidilebilir.
 *
 * Her adim tuvalin degil, katman listelerinin bir kopyasi - yuzlerce
 * noktali cizgiler birikince bellek buyur. Yirmi dort, bir remix
 * oturumunda yapilan islem sayisinin epey ustunde.
 */
export const GECMIS_SINIRI = 24;

/**
 * Bir islem *yapilmadan once* ki durumu yigina koyar.
 *
 * Cagrilma ani onemli: cizgi tamamlandiginda degil, `pointerdown`
 * aninda. Boylece geri alma cizgiyi butun halinde kaldirir, son
 * noktasini degil.
 */
export function gecmiseYaz(
  gecmis: DuzenlemeDurumu[],
  durum: DuzenlemeDurumu,
  sinir: number = GECMIS_SINIRI,
): DuzenlemeDurumu[] {
  // Sig kopya yeterli: bilesende hem `strokes` hem `texts` her zaman
  // yeni dizi uretilerek guncelleniyor, mevcut ogeler degistirilmiyor.
  const yeni = [...gecmis, { strokes: [...durum.strokes], texts: [...durum.texts] }];
  return yeni.length > sinir ? yeni.slice(yeni.length - sinir) : yeni;
}

/**
 * Son durumu yigindan cikarir.
 *
 * Yigin bossa `durum` null doner - cagiran taraf o zaman hicbir sey
 * yapmaz ve dugme zaten pasiftir.
 */
export function gecmistenAl(gecmis: DuzenlemeDurumu[]): {
  gecmis: DuzenlemeDurumu[];
  durum: DuzenlemeDurumu | null;
} {
  if (gecmis.length === 0) return { gecmis, durum: null };
  return {
    gecmis: gecmis.slice(0, -1),
    durum: gecmis[gecmis.length - 1],
  };
}
