/**
 * Hata siniri.
 *
 * React'te bir bilesen render sirasinda hata firlatirsa, yakalanmazsa
 * React tum agaci soker: ekranda **bembeyaz bir sayfa** kalir. Juri
 * demosunda bunun bedeli buyuk - urun calismiyor gorunur ve geri
 * donusu yok, cunku gezinme cubugu da gitmistir.
 *
 * Sinir bilerek `Sayfalar`'in etrafina konuyor, uygulamanin en disina
 * degil: boylece bir sayfa patlasa bile baslik, gezinme ve kullanici
 * secici ayakta kalir ve kullanici baska bir ekrana gecerek demoya
 * devam edebilir. Rota degisince sinir `key` ile sifirlaniyor.
 *
 * Sinif bileseni: `getDerivedStateFromError` / `componentDidCatch`
 * kancalarla karsiligi olmayan iki API - React 19'da da hata siniri
 * yazmanin tek yolu sinif.
 */
import { Component, type ErrorInfo, type ReactNode } from "react";
import { Button, Panel } from "./ui";

type Props = { children: ReactNode };
type State = { hata: Error | null };

export class HataSiniri extends Component<Props, State> {
  state: State = { hata: null };

  static getDerivedStateFromError(hata: Error): State {
    return { hata };
  }

  componentDidCatch(hata: Error, bilgi: ErrorInfo) {
    // Ekranda ham yigin izi gostermiyoruz ama konsola birakiyoruz:
    // demoda bir sey patlarsa sebebi tarayici konsolunda duruyor.
    console.error("Arayuzde yakalanmis hata:", hata, bilgi.componentStack);
  }

  render() {
    const { hata } = this.state;
    if (!hata) return this.props.children;

    return (
      <Panel title="Bu ekran açılamadı">
        <div role="alert" className="space-y-4">
          <p className="text-[13.5px] leading-relaxed text-[var(--color-ink)]">
            Beklenmedik bir sorun oluştu ve bu bölüm çizilemedi. Diğer
            ekranlar çalışmaya devam ediyor; üstteki gezinmeden başka bir
            sayfaya geçebilir ya da buradan yeniden deneyebilirsiniz.
          </p>

          <div className="flex flex-wrap gap-2">
            <Button
              variant="primary"
              onClick={() => this.setState({ hata: null })}
            >
              Yeniden dene
            </Button>
            <Button onClick={() => window.location.reload()}>
              Sayfayı yenile
            </Button>
          </div>

          {/* Juri ekrani gorurken yigin izi dokulmesin diye kapali;
              gerektiginde acilabiliyor. */}
          <details className="text-[12px] text-[var(--color-ink-3)]">
            <summary className="cursor-pointer">Teknik ayrıntı</summary>
            <p className="num mt-2 leading-relaxed break-words">
              {hata.message || String(hata)}
            </p>
          </details>
        </div>
      </Panel>
    );
  }
}
