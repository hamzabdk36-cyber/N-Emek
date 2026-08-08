/**
 * Paylasilan arayuz ilkelleri.
 *
 * Renk disiplini: altin = para/pay, yesil = dogrulanmis, turuncu = orta
 * guven, kirmizi = dusuk guven/itiraz, mavi = zincir/baglanti. Bu
 * eslesme tum ekranlarda ayni; kullanici bir rengi bir kez ogrenince
 * her yerde okuyabiliyor.
 */
import type { ReactNode } from "react";
import type { ConfidenceBand } from "../api";

/* -------------------------------------------------------------------------- */
export function Panel({
  title,
  subtitle,
  right,
  children,
  className = "",
}: {
  title?: ReactNode;
  subtitle?: ReactNode;
  right?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel overflow-hidden ${className}`}>
      {(title || right) && (
        <header className="flex items-start justify-between gap-4 border-b border-[var(--color-line-soft)] px-5 py-3.5">
          <div className="min-w-0">
            {title && (
              <h2 className="text-[13px] font-semibold tracking-wide text-[var(--color-ink)] uppercase">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="mt-1 text-[13px] leading-relaxed text-[var(--color-ink-2)]">
                {subtitle}
              </p>
            )}
          </div>
          {right && <div className="shrink-0">{right}</div>}
        </header>
      )}
      <div className="px-5 py-4">{children}</div>
    </section>
  );
}

/* -------------------------------------------------------------------------- */
type Tone = "neutral" | "gold" | "verify" | "caution" | "alert" | "link";

const TONES: Record<Tone, string> = {
  neutral:
    "bg-[var(--color-surface-2)] text-[var(--color-ink-2)] border-[var(--color-line)]",
  gold: "bg-[var(--color-gold-dim)]/40 text-[var(--color-gold)] border-[var(--color-gold)]/35",
  verify:
    "bg-[var(--color-verify-dim)]/50 text-[var(--color-verify)] border-[var(--color-verify)]/35",
  caution:
    "bg-[var(--color-caution-dim)]/50 text-[var(--color-caution)] border-[var(--color-caution)]/35",
  alert:
    "bg-[var(--color-alert-dim)]/50 text-[var(--color-alert)] border-[var(--color-alert)]/35",
  link: "bg-[var(--color-link-dim)]/50 text-[var(--color-link)] border-[var(--color-link)]/35",
};

export function Badge({
  tone = "neutral",
  children,
  title,
}: {
  tone?: Tone;
  children: ReactNode;
  title?: string;
}) {
  return (
    <span
      title={title}
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium whitespace-nowrap ${TONES[tone]}`}
    >
      {children}
    </span>
  );
}

const BAND_TONE: Record<string, Tone> = {
  yuksek: "verify",
  orta: "caution",
  dusuk: "alert",
};
const BAND_LABEL: Record<string, string> = {
  yuksek: "Yüksek güven",
  orta: "Orta güven",
  dusuk: "Düşük güven",
};

export function ConfidenceBadge({ band }: { band: ConfidenceBand }) {
  return (
    <Badge tone={BAND_TONE[band.level] ?? "neutral"} title={band.note}>
      <Dot />
      {BAND_LABEL[band.level] ?? band.level}
      <span className="num opacity-70">{band.score.toFixed(2)}</span>
    </Badge>
  );
}

function Dot() {
  return <span className="h-1.5 w-1.5 rounded-full bg-current" />;
}

/* -------------------------------------------------------------------------- */
export function Stat({
  label,
  value,
  hint,
  tone = "neutral",
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  tone?: Tone;
}) {
  const color =
    tone === "gold"
      ? "text-[var(--color-gold)]"
      : tone === "verify"
        ? "text-[var(--color-verify)]"
        : "text-[var(--color-ink)]";
  return (
    <div className="min-w-0">
      <div className="text-[11px] font-medium tracking-wide text-[var(--color-ink-3)] uppercase">
        {label}
      </div>
      <div className={`num mt-1 text-xl leading-tight font-semibold ${color}`}>
        {value}
      </div>
      {hint && (
        <div className="mt-0.5 text-[12px] text-[var(--color-ink-3)]">{hint}</div>
      )}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/** Pay dagilimini tek bir yatay serit olarak gosterir. */
export function ShareBar({
  segments,
}: {
  segments: { label: string; value: number; color: string }[];
}) {
  const total = segments.reduce((sum, s) => sum + s.value, 0) || 1;
  return (
    <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-[var(--color-surface-2)]">
      {segments.map((s, i) => (
        <div
          key={i}
          className="h-full transition-[width] duration-500"
          style={{ width: `${(s.value / total) * 100}%`, background: s.color }}
          title={`${s.label}: ${((s.value / total) * 100).toFixed(1)}%`}
        />
      ))}
    </div>
  );
}

/** Rol -> renk. Pay serilerinde ve zincir grafiginde ayni eslesme. */
export function roleColor(role: string, index = 0): string {
  if (role === "creator") return "#f2b134";
  if (role === "platform") return "#3a4250";
  const palette = ["#5b8def", "#3fbf7f", "#b47ae0", "#e0954a", "#5cc9c4"];
  return palette[index % palette.length];
}

/* -------------------------------------------------------------------------- */
export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-[13px] text-[var(--color-ink-2)]">
      <span
        className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-[var(--color-line)] border-t-[var(--color-link)]"
        role="status"
        aria-label="Yükleniyor"
      />
      {label}
    </div>
  );
}

export function EmptyState({
  title,
  hint,
  action,
}: {
  title: string;
  hint?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-center">
      <p className="text-[15px] font-medium text-[var(--color-ink-2)]">{title}</p>
      {hint && (
        <p className="max-w-md text-[13px] leading-relaxed text-[var(--color-ink-3)]">
          {hint}
        </p>
      )}
      {action}
    </div>
  );
}

export function ErrorNote({ error }: { error: string }) {
  return (
    <div className="rounded-lg border border-[var(--color-alert)]/40 bg-[var(--color-alert-dim)]/40 px-4 py-3 text-[13px] text-[var(--color-alert)]">
      {error}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
export function Button({
  children,
  onClick,
  variant = "default",
  disabled,
  type = "button",
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "default" | "primary" | "ghost" | "danger";
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}) {
  const styles: Record<string, string> = {
    default:
      "bg-[var(--color-surface-2)] text-[var(--color-ink)] border-[var(--color-line)] hover:border-[#3a4250]",
    primary:
      "bg-[var(--color-gold)] text-[#0a0c0f] border-transparent hover:bg-[#ffc255]",
    ghost:
      "bg-transparent text-[var(--color-ink-2)] border-transparent hover:bg-[var(--color-surface-2)] hover:text-[var(--color-ink)]",
    danger:
      "bg-transparent text-[var(--color-alert)] border-[var(--color-alert)]/40 hover:bg-[var(--color-alert-dim)]/40",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-lg border px-3.5 py-2 text-[13px] font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-45 ${styles[variant]} ${className}`}
    >
      {children}
    </button>
  );
}

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-[12px] font-medium text-[var(--color-ink-2)]">
        {label}
      </span>
      <div className="mt-1.5">{children}</div>
      {hint && (
        <span className="mt-1 block text-[11px] text-[var(--color-ink-3)]">
          {hint}
        </span>
      )}
    </label>
  );
}

export const inputClass =
  "w-full rounded-lg border border-[var(--color-line)] bg-[var(--color-bg)] px-3 py-2 text-[13px] text-[var(--color-ink)] placeholder:text-[var(--color-ink-3)] focus:border-[var(--color-link)] focus:outline-none";

/* -------------------------------------------------------------------------- */
export function Avatar({
  name,
  accent,
  size = 28,
}: {
  name: string;
  accent: string;
  size?: number;
}) {
  const initials = name
    .split(" ")
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase();
  return (
    <span
      className="inline-flex shrink-0 items-center justify-center rounded-full font-semibold"
      style={{
        width: size,
        height: size,
        background: `${accent}22`,
        color: accent,
        border: `1px solid ${accent}55`,
        fontSize: size * 0.38,
      }}
      aria-hidden
    >
      {initials}
    </span>
  );
}
