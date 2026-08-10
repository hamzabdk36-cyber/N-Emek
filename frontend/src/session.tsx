/**
 * Demo oturumu.
 *
 * Gercek kimlik dogrulama prototipin kapsaminda degil; jurinin
 * "Ayse olarak bak, sonra Ceyda olarak bak" diyebilmesi icin basit bir
 * aktor secici yeterli. Secim localStorage'da tutulur ki sayfa
 * yenilenince demo bozulmasin.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, type Health, type User } from "./api";

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

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([api.users(), api.health().catch(() => null)])
      .then(([list, h]) => {
        if (cancelled) return;
        setUsers(list);
        setHealth(h);
        const saved = localStorage.getItem(STORAGE_KEY);
        setUser(list.find((u) => u.id === saved) ?? list[0] ?? null);
      })
      .catch(() => {
        // Backend kapaliysa oturum bos kalir; sayfalar kendi hata
        // notlarini gosterir. Yakalanmadan birakilirsa bu bir
        // "unhandled rejection" olarak konsola dusuyordu - demoda
        // konsolun temiz olmasi gereken tek an juri onunde.
        if (!cancelled) setUsers([]);
      })
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [tick]);

  const setCurrentUser = useCallback((user: User) => {
    localStorage.setItem(STORAGE_KEY, user.id);
    setUser(user);
  }, []);

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
