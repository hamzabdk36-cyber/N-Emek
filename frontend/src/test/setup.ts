/**
 * Vitest kurulum dosyasi - her test dosyasindan once calisir.
 *
 * `jest-dom/vitest` hem esleyicileri (`toBeInTheDocument` vb.) hem de
 * tip genisletmesini getiriyor; bu dosya `tsconfig`'in "src" kapsaminda
 * oldugu icin `tsc --noEmit` de esleyicileri taniyor.
 */
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Testler ayni jsdom belgesini paylasiyor; temizlenmezse bir onceki
// testin agaci `getBy*` sorgularina "birden fazla eslesme" dedirtiyor.
afterEach(cleanup);
