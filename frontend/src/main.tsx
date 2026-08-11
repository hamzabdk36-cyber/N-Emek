import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
// Yazi tipleri pakette; CDN yok, cevrimdisi ve Docker'da calisiyor.
//
// Onceden `theme.css` bu iki aileyi *istiyor* ama hicbir yerde
// yuklemiyordu: ne @font-face vardi ne bir baglanti. Yani tasarim
// kararinin tamami yedege dusuyordu (Windows'ta Segoe UI + Consolas) ve
// bu, uretilen paket incelenmeden gorulmuyordu.
//
// Paketin `index.css`'i yedi altkumeyi ayri @font-face olarak taniyor;
// tarayici `unicode-range` sayesinde yalnizca ihtiyaci olani indiriyor.
// Turkce icin ikisi birden gerekiyor ve ikisi de burada:
//   latin      -> ç ö ü ve *ı* (U+0131)
//   latin-ext  -> ğ Ğ ş Ş ve *İ* (U+0130)
// Yalnizca latin alinsaydi ayni satirda iki farkli yazi tipi karisirdi.
import "@fontsource-variable/inter";
import "@fontsource-variable/jetbrains-mono";
import "./theme.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
