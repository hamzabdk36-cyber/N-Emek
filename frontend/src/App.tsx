import { NavLink, Route, Routes } from "react-router-dom";
import { Avatar } from "./components/ui";
import { SessionProvider, useSession } from "./session";
import Feed from "./pages/Feed";
import ContentDetail from "./pages/ContentDetail";
import RemixStudio from "./pages/RemixStudio";
import Verify from "./pages/Verify";
import Campaigns from "./pages/Campaigns";
import Moderation from "./pages/Moderation";

const NAV = [
  { to: "/", label: "Akış", end: true },
  { to: "/kaynak-bul", label: "Kaynak bul" },
  { to: "/kampanyalar", label: "Kampanyalar" },
  { to: "/inceleme", label: "İnceleme kuyruğu" },
];

export default function App() {
  return (
    <SessionProvider>
      <div className="min-h-dvh">
        <Header />
        <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
          <Routes>
            <Route path="/" element={<Feed />} />
            <Route path="/icerik/:id" element={<ContentDetail />} />
            <Route path="/remix/:id" element={<RemixStudio />} />
            <Route path="/kaynak-bul" element={<Verify />} />
            <Route path="/kampanyalar" element={<Campaigns />} />
            <Route path="/inceleme" element={<Moderation />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </SessionProvider>
  );
}

function Header() {
  const { users, currentUser, setCurrentUser, health } = useSession();

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--color-line)] bg-[var(--color-bg)]/92 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-3 px-4 py-3 sm:px-6">
        <NavLink to="/" className="flex items-center gap-2.5">
          <Logo />
          <span className="leading-tight">
            <span className="block text-[15px] font-semibold tracking-tight">
              N-Emek
            </span>
            <span className="block text-[10.5px] tracking-wide text-[var(--color-ink-3)] uppercase">
              N'Sosyal emek katmanı
            </span>
          </span>
        </NavLink>

        <nav className="flex items-center gap-1" aria-label="Ana gezinme">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `rounded-lg px-3 py-1.5 text-[13px] font-medium transition-colors ${
                  isActive
                    ? "bg-[var(--color-surface-2)] text-[var(--color-ink)]"
                    : "text-[var(--color-ink-2)] hover:text-[var(--color-ink)]"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          {health && (
            <span
              className="hidden items-center gap-1.5 text-[11px] text-[var(--color-ink-3)] md:flex"
              title={`${health.indexed_contents} içerik indekslendi · ${health.device} · C2PA imzalama ${health.c2pa_signing ? "açık" : "kapalı"}`}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-verify)]" />
              {health.indexed_contents} içerik · {health.device}
            </span>
          )}
          {currentUser && (
            <label className="flex items-center gap-2">
              <span className="sr-only">Hangi kullanıcı olarak görüntüleniyor</span>
              <Avatar name={currentUser.display_name} accent={currentUser.accent} />
              <select
                value={currentUser.id}
                onChange={(e) => {
                  const next = users.find((u) => u.id === e.target.value);
                  if (next) setCurrentUser(next);
                }}
                className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] px-2.5 py-1.5 text-[13px] text-[var(--color-ink)] focus:border-[var(--color-link)] focus:outline-none"
              >
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.display_name}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
      </div>
    </header>
  );
}

function Logo() {
  return (
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden>
      <rect width="26" height="26" rx="7" fill="#12151a" stroke="#242932" />
      {/* "N" harfi: sol dikey, capraz, sag dikey */}
      <path
        d="M8 19V7l10 12V7"
        stroke="#f2b134"
        strokeWidth="2.1"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Footer() {
  return (
    <footer className="mx-auto max-w-6xl px-4 py-8 text-[11.5px] leading-relaxed text-[var(--color-ink-3)] sm:px-6">
      N-Emek · TEKNOFEST 2026 NSosyal İnovasyon Yarışması, İçerik Ekonomisi.
      Sistem sahiplik kararı vermez; kanıtlarıyla birlikte bir zincir önerisi
      sunar ve her öneri itiraza açıktır.
    </footer>
  );
}
