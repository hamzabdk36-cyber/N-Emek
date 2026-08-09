#!/bin/sh
# N-Emek backend acilis betigi.
#
# Kapsayici ilk kez ayaga kalktiginda uc sey eksik olur: imzalama
# sertifikalari, test gorseli korpusu ve demo verisi. Bunlarin hicbiri
# depoya konmaz (sertifikalar gizli, korpus 100 MB) ve juri makinesinde
# elle uretilmelerini beklemek "tek komutla kurulum" sozunu bozar.
#
# Betik her adimi *yalnizca eksikse* yapar; ikinci `docker compose up`
# hizli acilir. Uretilenler birim (volume) uzerinde kalici.
set -e

CORPUS_COUNT="${NEMEK_CORPUS_COUNT:-24}"

echo "N-Emek | acilis hazirligi"

# 1. C2PA imzalama sertifikalari
if [ ! -f /app/backend/certs/private.key ]; then
    echo "  sertifikalar uretiliyor..."
    python scripts/gen_dev_certs.py
else
    echo "  sertifikalar zaten var"
fi

# 2. Gorsel korpusu. Demo senaryosu en az 4 gorsel istiyor; varsayilan 24
#    hem hizli iniyor hem indeksin bos olmadigini gosteriyor. Tam
#    degerlendirme kosacaksaniz NEMEK_CORPUS_COUNT=320 verin.
if [ -z "$(ls -A /app/data/raw 2>/dev/null)" ]; then
    echo "  korpus indiriliyor ($CORPUS_COUNT gorsel)..."
    python scripts/fetch_eval_images.py "$CORPUS_COUNT" || \
        echo "  UYARI: korpus indirilemedi (internet yok?); demo verisi kurulamayacak"
else
    echo "  korpus zaten var"
fi

# 3. Demo verisi (altin senaryo)
if [ ! -f /app/data/nemek.db ] && [ -n "$(ls -A /app/data/raw 2>/dev/null)" ]; then
    echo "  altin senaryo kuruluyor..."
    python scripts/seed_demo.py --reset
else
    echo "  demo verisi zaten var (sifirlamak icin: docker compose down -v)"
fi

echo "N-Emek | API baslatiliyor -> http://localhost:8000"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
