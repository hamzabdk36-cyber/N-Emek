@echo off
chcp 65001 >nul
setlocal
title N-Emek kurulum

rem Bos bir Windows makinede Docker'siz kurulum: Python, Node, bagimliliklar,
rem sertifikalar, test gorselleri, demo verisi. Her adim yalnizca eksikse
rem yapilir; yarida kalirsa tekrar cift tiklamak yeter. Bittiginde demoyu
rem demo_baslat.bat acar. Elle kurulum adimlari: BASLARKEN.md

set "ROOT=%~dp0"
cd /d "%ROOT%"
set "PY=%ROOT%.venv\Scripts\python.exe"
set "YENIDEN="

echo.
echo === N-Emek kurulum ===
echo İlk kurulum 10-20 dakika sürer, ~5 GB disk ve internet ister.
echo.

rem --- 1. Python 3.13 -----------------------------------------------------------
rem `python` yerine `py` baslaticisi: Windows'ta Store'un sahte python.exe
rem takma adi kurulu olmadigi halde "var" gibi gorunuyor.
if exist "%PY%" goto :python_tamam
py -3.13 --version >nul 2>&1 && goto :python_tamam
echo [..] Python 3.13 kuruluyor
call :winget Python.Python.3.13 "https://www.python.org/downloads/"
if errorlevel 1 goto :hata
set "YENIDEN=1"
goto :node
:python_tamam
echo [tamam] Python 3.13

rem --- 2. Node ------------------------------------------------------------------
:node
where node >nul 2>&1 && goto :node_tamam
echo [..] Node.js kuruluyor
call :winget OpenJS.NodeJS.LTS "https://nodejs.org/"
if errorlevel 1 goto :hata
set "YENIDEN=1"
goto :yol_kontrol
:node_tamam
for /f "delims=" %%v in ('node --version') do echo [tamam] Node %%v

rem winget PATH'i yalnizca yeni acilan pencerelere yansitiyor.
:yol_kontrol
if defined YENIDEN (
  echo.
  echo ##########################################################
  echo #  Python/Node kuruldu. Bu pencereyi KAPATIN ve          #
  echo #  kurulum.bat'a yeniden çift tıklayın.                  #
  echo ##########################################################
  echo.
  pause
  exit /b 0
)

rem --- 3. Python sanal ortami ---------------------------------------------------
if exist "%PY%" (
  echo [tamam] .venv zaten var
) else (
  echo [..] .venv oluşturuluyor
  py -3.13 -m venv .venv || goto :hata
  "%PY%" -m pip install --upgrade pip || goto :hata
  echo [tamam] .venv
)

rem --- 4. PyTorch, requirements'tan ONCE ----------------------------------------
rem Ters sirada open_clip_torch torch'u varsayilan PyPI'den ceker ve sonraki
rem kurulum "zaten var" deyip gecer (bkz. backend/Dockerfile).
"%PY%" -c "import torch" >nul 2>&1 && (
  echo [tamam] PyTorch zaten kurulu
  goto :bagimliliklar
)
set "TORCH_IDX=https://download.pytorch.org/whl/cpu"
nvidia-smi >nul 2>&1 && set "TORCH_IDX=https://download.pytorch.org/whl/cu126"
echo [..] PyTorch kuruluyor (%TORCH_IDX%)
"%PY%" -m pip install torch torchvision --index-url %TORCH_IDX% || goto :hata
echo [tamam] PyTorch

rem --- 5. Backend bagimliliklari ------------------------------------------------
:bagimliliklar
echo [..] Backend bağımlılıkları denetleniyor
"%PY%" -m pip install -q -r backend\requirements.txt || goto :hata
echo [tamam] Backend bağımlılıkları

rem --- 6. Arayuz paketleri ------------------------------------------------------
if exist "frontend\node_modules" (
  echo [tamam] frontend\node_modules zaten var
) else (
  echo [..] Arayüz paketleri kuruluyor
  pushd frontend
  call npm install || (popd & goto :hata)
  popd
  echo [tamam] Arayüz paketleri
)

rem --- 7. C2PA gelistirme sertifikalari -----------------------------------------
if exist "backend\certs\private.key" (
  echo [tamam] Sertifikalar zaten var
) else (
  echo [..] Sertifikalar üretiliyor
  "%PY%" scripts\gen_dev_certs.py || goto :hata
  echo [tamam] Sertifikalar
)

rem --- 8. Test gorselleri (Docker varsayilaniyla ayni: 24) ----------------------
dir /b "data\raw" 2>nul | findstr . >nul && (
  echo [tamam] Test görselleri zaten var
  goto :demo_verisi
)
echo [..] Test görselleri indiriliyor
"%PY%" scripts\fetch_eval_images.py 24 || goto :hata
echo [tamam] Test görselleri

rem --- 9. Demo verisi -----------------------------------------------------------
rem Ilk calistirmada CLIP modeli de iner (~600 MB, bir kez).
:demo_verisi
if exist "data\nemek.db" (
  echo [tamam] Demo veritabanı zaten var ^(sıfırlamak için: .venv\Scripts\python.exe scripts\seed_demo.py --reset^)
) else (
  echo [..] Demo senaryosu kuruluyor ^(ilk seferde yapay zekâ modeli iner, birkaç dakika sürer^)
  "%PY%" scripts\seed_demo.py --reset || goto :hata
  echo [tamam] Demo verisi
)

rem --- 10. Model onbellegi: demo_baslat.bat cevrimdisi calisiyor -----------------
if not exist "%USERPROFILE%\.cache\huggingface\hub\models--laion--CLIP-ViT-B-32-laion2B-s34B-b79K" (
  echo [uyarı] CLIP modeli önbellekte bulunamadı; demo_baslat.bat bunu ister.
  echo         İnternet varken kurulum.bat'ı yeniden çalıştırın.
  goto :hata
)
echo [tamam] CLIP modeli önbellekte

echo.
echo ##########################################################
echo #  KURULUM TAMAM                                         #
echo #  Demoyu açmak için demo_baslat.bat'a çift tıklayın     #
echo #  Tarayıcı: http://localhost:5173                       #
echo ##########################################################
echo.
pause
exit /b 0

rem --- Yardimci: winget ile kur, yoksa elle kurulum adresini soyle ---------------
:winget
where winget >nul 2>&1 || (
  echo [HATA] winget yok. Elle kurun: %~2
  echo        Kurulumda "Add to PATH" kutusunu işaretleyin, sonra bu betiği yeniden çalıştırın.
  exit /b 1
)
winget install -e --id %1 --scope user --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  rem Bazi paketler kullanici kapsamini desteklemiyor; makine kapsamini dene.
  winget install -e --id %1 --accept-package-agreements --accept-source-agreements
)
if errorlevel 1 (
  echo [HATA] %1 kurulamadı. Elle kurun: %~2
  exit /b 1
)
exit /b 0

:hata
echo.
echo [HATA] Kurulum yarıda kaldı. Yukarıdaki mesaja bakın; sorunu giderip
echo        kurulum.bat'ı yeniden çalıştırın, tamamlanan adımlar atlanır.
echo.
pause
exit /b 1
