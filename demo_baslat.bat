@echo off
chcp 65001 >nul
setlocal
title N-Emek demo

rem Canli demoyu tek tikla ayaga kaldirir: backend + arayuz + model isitma + sekmeler.
rem Veritabanina dokunmaz (seed_demo.py --reset CAGRILMAZ). Durdurmak icin acilan
rem iki pencereyi kapatmak yeter. Ayrintilar: docs\DEMO-SENARYOSU.md

set "ROOT=%~dp0"
if not exist "%ROOT%backend\app\main.py" set "ROOT=C:\Users\HAMZA\Desktop\n-emek\n-emk\N-Emek\"
cd /d "%ROOT%"

set "PY=%ROOT%.venv\Scripts\python.exe"
set "API=http://127.0.0.1:8000"
set "WEB=http://localhost:5173"

echo.
echo === N-Emek canlı demo ===
echo.

rem --- On denetim -------------------------------------------------------------
if not exist "%PY%" (
  echo [HATA] .venv bulunamadı: %PY%
  goto :hata
)
if not exist "data\nemek.db" (
  echo [HATA] Demo veritabanı yok: data\nemek.db
  goto :hata
)
if not exist "frontend\node_modules" (
  echo [HATA] frontend\node_modules yok. İnternet varken: cd frontend ^&^& npm install
  goto :hata
)
if not exist "%USERPROFILE%\.cache\huggingface\hub\models--laion--CLIP-ViT-B-32-laion2B-s34B-b79K" (
  echo [HATA] CLIP modeli önbellekte yok. İnternet varken bir kez demo_hazirla.py çalıştırın.
  goto :hata
)
echo [tamam] Ön denetim

rem --- Cevrimdisi: model yerel onbellekten, aga cikmayi denemez -----------------
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1

rem --- Backend (--reload YOK) ---------------------------------------------------
"%SystemRoot%\System32\curl.exe" -s -f -o nul "%API%/api/health" && (
  echo [tamam] Backend zaten çalışıyor, yeniden kullanılıyor
  goto :arayuz
)
echo [..] Backend başlatılıyor
start "N-Emek backend" cmd /k ""%PY%" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
set /a SAY=0
:backend_bekle
"%SystemRoot%\System32\timeout.exe" /t 1 /nobreak >nul
"%SystemRoot%\System32\curl.exe" -s -f -o nul "%API%/api/health" && goto :backend_hazir
set /a SAY+=1
if %SAY% geq 60 (
  echo [HATA] Backend 60 sn içinde açılmadı. "N-Emek backend" penceresindeki hataya bakın.
  goto :hata
)
goto :backend_bekle
:backend_hazir
echo [tamam] Backend hazır (~%SAY% sn)

rem --- Arayuz -------------------------------------------------------------------
:arayuz
"%SystemRoot%\System32\curl.exe" -s -f -o nul "%WEB%/" && (
  echo [tamam] Arayüz zaten çalışıyor, yeniden kullanılıyor
  goto :isit
)
echo [..] Arayüz başlatılıyor
start "N-Emek arayuz" /d "%ROOT%frontend" cmd /k npm run dev
set /a SAY=0
:arayuz_bekle
"%SystemRoot%\System32\timeout.exe" /t 1 /nobreak >nul
"%SystemRoot%\System32\curl.exe" -s -f -o nul "%WEB%/" && goto :arayuz_hazir
set /a SAY+=1
if %SAY% geq 60 (
  echo [HATA] Arayüz 60 sn içinde açılmadı. "N-Emek arayuz" penceresine bakın.
  goto :hata
)
goto :arayuz_bekle
:arayuz_hazir
echo [tamam] Arayüz hazır (~%SAY% sn)

rem --- Model isitma ve denetim -------------------------------------------------
:isit
echo.
echo [..] Model ısıtılıyor ve demo denetleniyor
echo.
"%PY%" scripts\demo_hazirla.py
set "SONUC=%errorlevel%"
echo.
if "%SONUC%"=="0" (
  echo ##########################################
  echo #                 HAZIR                  #
  echo ##########################################
) else (
  echo ##########################################
  echo #   HAZIR DEĞİL - canlı sorgu adımını    #
  echo #   atla, Emek Kartı turunu yap          #
  echo ##########################################
)

rem --- Sekmeler: Akis, "Bulduğum kare" Emek Karti, Kaynak bul ----------------------
set "KART="
for /f "usebackq delims=" %%i in (`call "%PY%" -c "import json,urllib.request as u;print(next((c['id'] for c in json.load(u.urlopen('%API%/api/feed')) if c['title'].startswith('Buldu')),''))"`) do set "KART=%%i"
start "" "%WEB%/"
if defined KART (
  start "" "%WEB%/icerik/%KART%"
) else (
  echo [uyarı] "Bulduğum kare" akışta bulunamadı, Emek Kartı sekmesini elle açın.
)
start "" "%WEB%/kaynak-bul"

echo.
echo Kalan elle adımlar:
echo   - Kullanıcı seçici: Ayşe Yılmaz
echo   - F11 tam ekran, yakınlaştırma %%100
echo   - Win+P: Çoğalt · bildirimler kapalı · şarj takılı
echo   - Dosya penceresini bir kez data\demo klasöründe aç
echo.
echo Durdurmak için "N-Emek backend" ve "N-Emek arayuz" pencerelerini kapatın.
echo.
pause
exit /b 0

:hata
echo.
pause
exit /b 1
