<#
.SYNOPSIS
    Uretilen sunumu PowerPoint'e cizdirir: metin tasmasi denetlenir,
    her sayfanin PNG onizlemesi alinir, istenirse PDF uretilir.

.DESCRIPTION
    Neden var
    ---------
    python-pptx metni cizmez; bir kutunun tasip tasmadigi ancak yazi
    gercekten dizildiginde belli olur. Teslim de PDF olarak yapiliyor
    ve sablon 75 MB siniri koyuyor. Makinede PowerPoint kurulu oldugu
    icin isi ona yaptiriyoruz (`rapor_word.ps1` ile ayni kalip).

    Tasma denetimi yalnizca `sunum_pptx.py`'nin ekledigi sekillerde
    ("NEMEK " onekli) yapilir: sablonun kendi kutulari otomatik boyutlu,
    orada kutu yuksekligi zaten metne gore buyuyor.

    Onizlemeler `docs/SUNUM/onizleme/` altina yazilir; her sayfa gozle
    kontrol edilmeden teslim edilmez.

.PARAMETER Dosya
    Uretilmis .pptx. Varsayilan: docs/SUNUM/N-Emek-Sunum.pptx

.PARAMETER Pdf
    PDF de uretilsin mi. Teslim oncesi acilir.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/sunum_powerpoint.ps1
    powershell -ExecutionPolicy Bypass -File scripts/sunum_powerpoint.ps1 -Pdf
#>
param(
    [string]$Dosya = "",
    [switch]$Pdf
)

$ErrorActionPreference = "Stop"
$kok = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrEmpty($Dosya)) {
    $Dosya = Join-Path $kok "docs\SUNUM\N-Emek-Sunum.pptx"
}
if (-not (Test-Path $Dosya)) {
    Write-Output "bulunamadi: $Dosya"
    Write-Output "  once: .venv\Scripts\python.exe scripts\sunum_pptx.py"
    exit 2
}
$Dosya = (Resolve-Path $Dosya).Path
$onizleme = Join-Path (Split-Path -Parent $Dosya) "onizleme"

$SAYFA_SINIRI = 19
$MB_SINIRI = 75
# PowerPoint olculeri punto cinsinden; yarim puntoluk fark yuvarlamadir.
$TOLERANS = 0.5

# Dosya PowerPoint'te acikken otomasyon bir iletisim kutusunda asili
# kalir. Kilidi onceden yoklayip anlasilir bir hatayla durmak iyi.
try {
    $akis = [System.IO.File]::Open($Dosya, "Open", "ReadWrite", "None")
    $akis.Close()
}
catch {
    Write-Output "dosya kilitli: $Dosya"
    Write-Output "  PowerPoint'te acik olabilir; kapatin."
    exit 2
}

New-Item -ItemType Directory -Force $onizleme | Out-Null
Get-ChildItem -Path $onizleme -Filter "*.png" | ForEach-Object { $_.Delete() }

$app = $null
$sunum = $null
$tasmalar = @()
try {
    $app = New-Object -ComObject PowerPoint.Application
    # ReadOnly, Untitled=false, WithWindow=false: gorunur pencere acilmaz.
    $sunum = $app.Presentations.Open($Dosya, -1, 0, 0)
    $sayfa = $sunum.Slides.Count

    foreach ($slayt in $sunum.Slides) {
        foreach ($sekil in $slayt.Shapes) {
            if (-not $sekil.Name.StartsWith("NEMEK ")) { continue }
            # Tablolar metne gore uzar; alt siniri adin sonunda "@cm" olarak
            # tasiyorlar (sunum_sayfalar.tablo). Satir yukseklikleri PowerPoint
            # diziliminden sonra okunur.
            if ($sekil.HasTable -and $sekil.Name -match "@([\d.]+)$") {
                $sinirPt = [double]::Parse($Matches[1], [Globalization.CultureInfo]::InvariantCulture) * 28.3465
                $yukseklik = 0.0
                foreach ($satir in $sekil.Table.Rows) { $yukseklik += $satir.Height }
                if ($sekil.Top + $yukseklik -gt $sinirPt + $TOLERANS) {
                    $tasmalar += ("sayfa {0,2}: {1} - tablo alti {2:N1} pt, sinir {3:N1} pt" -f `
                        $slayt.SlideIndex, $sekil.Name, ($sekil.Top + $yukseklik), $sinirPt)
                }
                continue
            }
            if (-not $sekil.HasTextFrame) { continue }
            $metin = $sekil.TextFrame2.TextRange
            if ($metin.Text.Length -eq 0) { continue }
            $cerceve = $sekil.TextFrame2
            $icYukseklik = $sekil.Height - $cerceve.MarginTop - $cerceve.MarginBottom
            if ($metin.BoundHeight -gt $icYukseklik + $TOLERANS) {
                $tasmalar += ("sayfa {0,2}: {1} - metin {2:N1} pt, kutu {3:N1} pt" -f `
                    $slayt.SlideIndex, $sekil.Name, $metin.BoundHeight, $icYukseklik)
            }
        }
        $slayt.Export((Join-Path $onizleme ("{0:D2}.png" -f $slayt.SlideIndex)), "PNG", 1920, 1080)
    }

    Write-Output "sayfa     : $sayfa / $SAYFA_SINIRI"
    Write-Output "onizleme  : $onizleme"

    if ($Pdf) {
        $pdfYolu = [System.IO.Path]::ChangeExtension($Dosya, ".pdf")
        # ppSaveAsPDF = 32
        $sunum.SaveAs($pdfYolu, 32)
        $mb = (Get-Item $pdfYolu).Length / 1MB
        Write-Output ("pdf       : {0} ({1:N1} MB / {2} MB)" -f $pdfYolu, $mb, $MB_SINIRI)
        if ($mb -gt $MB_SINIRI) {
            Write-Output "PDF BOYUT SINIRI ASILDI"
            exit 1
        }
    }
}
finally {
    try { if ($null -ne $sunum) { $sunum.Close() } } catch {}
    try { if ($null -ne $app) { $app.Quit() } } catch {}
    try {
        if ($null -ne $app) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
        }
    } catch {}
}

if ($tasmalar.Count -gt 0) {
    Write-Output ""
    Write-Output "METIN TASMASI: $($tasmalar.Count)"
    $tasmalar | ForEach-Object { Write-Output "  $_" }
    exit 1
}
if ($sayfa -gt $SAYFA_SINIRI) {
    Write-Output ""
    Write-Output "SAYFA SINIRI ASILDI: $sayfa > $SAYFA_SINIRI"
    exit 1
}
Write-Output "tasma     : yok"
