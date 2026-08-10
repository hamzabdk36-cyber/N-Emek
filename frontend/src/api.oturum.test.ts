/**
 * Jetonun istege gercekten eklenmesi ve 401'de oturumun yenilenmesi.
 *
 * Bu katman sessizce bozulabilir: jeton eklenmezse uclar 401 doner,
 * arayuz de hata notunu gosterir - yani ekranda "bir sey calismiyor"
 * gorunur ama sebebi gorunmez. Burada `fetch` sahtelenip gonderilen
 * basliga dogrudan bakiliyor.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api, setToken, setUnauthorizedHandler } from "./api";

function yanit(govde: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: String(status),
    json: async () => govde,
  } as Response;
}

/** Son cagrinin `Authorization` basligi. */
function gonderilenJeton(cagri: number = 0): string | null {
  const init = vi.mocked(fetch).mock.calls[cagri]?.[1];
  return new Headers(init?.headers).get("Authorization");
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
  setToken(null);
  setUnauthorizedHandler(null);
});

afterEach(() => {
  setToken(null);
  setUnauthorizedHandler(null);
  vi.unstubAllGlobals();
});

describe("jeton başlığı", () => {
  it("jeton yokken Authorization gönderilmiyor", async () => {
    vi.mocked(fetch).mockResolvedValue(yanit([]));

    await api.feed();

    expect(gonderilenJeton()).toBeNull();
  });

  it("jeton ayarlanınca her isteğe ekleniyor", async () => {
    vi.mocked(fetch).mockResolvedValue(yanit([]));
    setToken("abc.def");

    await api.feed();
    await api.campaigns();

    expect(gonderilenJeton(0)).toBe("Bearer abc.def");
    expect(gonderilenJeton(1)).toBe("Bearer abc.def");
  });

  it("mevcut başlıkları ezmiyor", async () => {
    vi.mocked(fetch).mockResolvedValue(yanit({}));
    setToken("abc.def");

    await api.setRevenue("c-1", 100);

    const init = vi.mocked(fetch).mock.calls[0][1];
    const headers = new Headers(init?.headers);
    expect(headers.get("Authorization")).toBe("Bearer abc.def");
    expect(headers.get("Content-Type")).toBe("application/json");
  });

  it("itiraz gövdesinde artık raiser_id yok", async () => {
    vi.mocked(fetch).mockResolvedValue(yanit({ id: "d-1", status: "open" }));
    setToken("abc.def");

    await api.openDispute("e-ab", "gerekçe");

    const govde = JSON.parse(
      String(vi.mocked(fetch).mock.calls[0][1]?.body),
    );
    expect(govde).toEqual({ edge_id: "e-ab", reason: "gerekçe" });
  });
});

describe("401 sonrası oturum yenileme", () => {
  it("yenileyici başarılı olursa istek bir kez daha deneniyor", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(yanit({ detail: "Oturum süresi doldu." }, 401))
      .mockResolvedValueOnce(yanit({ content_id: "c-1", revenue: 100 }));

    setToken("eski.jeton");
    const yenile = vi.fn(async () => {
      setToken("yeni.jeton");
      return true;
    });
    setUnauthorizedHandler(yenile);

    const sonuc = await api.setRevenue("c-1", 100);

    expect(yenile).toHaveBeenCalledTimes(1);
    expect(sonuc).toEqual({ content_id: "c-1", revenue: 100 });
    // İkinci deneme yeni jetonla gitti.
    expect(gonderilenJeton(0)).toBe("Bearer eski.jeton");
    expect(gonderilenJeton(1)).toBe("Bearer yeni.jeton");
  });

  it("yenileme başarısızsa hata kullanıcıya ulaşıyor", async () => {
    vi.mocked(fetch).mockResolvedValue(
      yanit({ detail: "Bu işlem için oturum gerekli." }, 401),
    );
    setUnauthorizedHandler(async () => false);

    await expect(api.setRevenue("c-1", 100)).rejects.toThrow(
      "Bu işlem için oturum gerekli.",
    );
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("sonsuz döngüye girmiyor: yenileme sonrası 401 yine gelirse durur", async () => {
    vi.mocked(fetch).mockResolvedValue(yanit({ detail: "Oturum gerekli." }, 401));
    const yenile = vi.fn(async () => true);
    setUnauthorizedHandler(yenile);

    await expect(api.setRevenue("c-1", 100)).rejects.toThrow("Oturum gerekli.");
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(yenile).toHaveBeenCalledTimes(1);
  });

  it("401 dışındaki hatalarda yenileme denenmiyor", async () => {
    vi.mocked(fetch).mockResolvedValue(
      yanit({ detail: "Geliri yalnızca içeriğin sahibi değiştirebilir." }, 403),
    );
    const yenile = vi.fn(async () => true);
    setUnauthorizedHandler(yenile);

    await expect(api.setRevenue("c-1", 100)).rejects.toThrow(
      "Geliri yalnızca içeriğin sahibi değiştirebilir.",
    );
    expect(yenile).not.toHaveBeenCalled();
  });
});
