/**
 * Demo oturumu.
 *
 * Gercek kimlik dogrulama prototipin kapsaminda degil; jurinin
 * "Ayse olarak bak, sonra Ceyda olarak bak" diyebilmesi icin basit bir
 * aktor secici yeterli. Secim localStorage'da tutulur ki sayfa
 * yenilenince demo bozulmasin.
 *
 * Aktor secmek artik ayni zamanda **oturum acmak**: secim yapilinca
 * arka planda `POST /api/oturum` cagrilir ve donen imzali jeton
 * saklanir. Ekranda gorunur bir degisiklik yok - secici ayni secici -
 * ama kullanici adina is yapan uclar (yukleme, remix, itiraz, gelir)
 * artik `owner_id` form alanina degil o jetona bakiyor. Onceden herkes
 * herkes adina icerik yukleyip baskasinin payina itiraz edebiliyordu.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  api,
  setToken,
  setUnauthorizedHandler,
  type Health,
  type User,
} from "./api";

interface SessionValue {
  users: User[];
  currentUser: User | null;
  setCurrentUser: (user: User) => void;
  health: Health | null;
  loading: boolean;
  refresh: () => void;
}

const SessionContext = createContext<SessionValue | null>(null);
const STORAGE_KEY = "nemek.actor";

export function SessionProvider({ children }: { children: ReactNode }) {
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setUser] = useState<User | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);

  // Jeton yenilemesi, o an secili kullaniciyi bilmeli. `ref` kullaniliyor
  // cunku yenileyici `api`'ye bir kez kuruluyor ve her secim
  // degisikliginde yeniden kurulmasi gereksiz.
  const aktifId = useRef<string | null>(null);

  const oturumAc = useCallback(async (user: User) => {
    aktifId.current = user.id;
    const oturum = await api.oturum(user.id);
    setToken(oturum.token);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([api.users(), api.health().catch(() => null)])
      .then(async ([list, h]) => {
        if (cancelled) return;
        setUsers(list);
        setHealth(h);
        const saved = localStorage.getItem(STORAGE_KEY);
        const secili = list.find((u) => u.id === saved) ?? list[0] ?? null;
        setUser(secili);
        // Jeton alinamazsa oturum jetonsuz kalir ama *kullanici listesi
        // silinmez*: liste zaten geldi. Ilk yazimda bu `catch` yoktu ve
        // oturum ucundaki bir hata asagidaki catch'e dusup listeyi de
        // bosaltiyordu - yani jeton hatasi tum arayuzu kullanicisiz
        // birakiyordu. Jetonsuz halde okuma ekranlari calisir; bir
        // mutasyon denendiginde 401 gelir ve oturum yenilenir.
        if (secili) await oturumAc(secili).catch(() => setToken(null));
      })
      .catch(() => {
        // Backend kapaliysa oturum bos kalir; sayfalar kendi hata
        // notlarini gosterir. Yakalanmadan birakilirsa bu bir
        // "unhandled rejection" olarak konsola dusuyordu - demoda
        // konsolun temiz olmasi gereken tek an juri onunde.
        if (!cancelled) {
          setUsers([]);
          setToken(null);
        }
      })
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [tick, oturumAc]);

  /**
   * Jeton suresi dolarsa ya da sunucu yeniden baslarsa (imzalama
   * anahtari surec basina uretiliyor) oturumu sessizce yeniler. Boylece
   * demonun ortasinda kullanici bir hata mesajina toslamiyor.
   */
  useEffect(() => {
    setUnauthorizedHandler(async () => {
      const id = aktifId.current;
      if (!id) return false;
      try {
        const oturum = await api.oturum(id);
        setToken(oturum.token);
        return true;
      } catch {
        setToken(null);
        return false;
      }
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const setCurrentUser = useCallback(
    (user: User) => {
      localStorage.setItem(STORAGE_KEY, user.id);
      setUser(user);
      // Jeton yenisi gelene kadar eskisi durmasin: aradaki kisa anda
      // yapilan bir istek onceki kullanici adina gitmesin.
      setToken(null);
      void oturumAc(user).catch(() => setToken(null));
    },
    [oturumAc],
  );

  const value = useMemo(
    () => ({
      users,
      currentUser,
      setCurrentUser,
      health,
      loading,
      refresh: () => setTick((t) => t + 1),
    }),
    [users, currentUser, setCurrentUser, health, loading],
  );

  return <SessionContext value={value}>{children}</SessionContext>;
}

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession, SessionProvider içinde çağrılmalı");
  return value;
}
