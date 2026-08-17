<#
.SYNOPSIS
    Uretilen raporu Word'e cizdirir: icindekiler guncellenir, sayfa
    sayisi olculur, PDF alinir.

.DESCRIPTION
    Neden var
    ---------
    Sablonun en sert kurali "en fazla 30 sayfa" ve bu sayi ancak belge
    gercekten cizildiginde belli olur - paragraf sayarak tahmin
    edilemez. Icindekiler de bir Word alani (`sdt`); sayfa numaralari
    yalnizca alan guncellenince olusur.

    python-docx ikisini de yapamaz. Makinede Word kurulu oldugu icin
    isi ona yaptiriyoruz.

    Cikti bilgi verir ama karar vermez: sayfa sayisi 30'u asarsa
    betik sifirdan farkli doner.

.PARAMETER Dosya
    Uretilmis .docx. Varsayilan: docs/RAPOR/N-Emek-Teknik-Rapor.docx

.PARAMETER Pdf
    PDF de uretilsin mi. Teslim oncesi acilir.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/rapor_word.ps1
    powershell -ExecutionPolicy Bypass -File scripts/rapor_word.ps1 -Pdf
#>
param(
    [string]$Dosya = "",
    [switch]$Pdf
)

$ErrorActionPreference = "Stop"
$kok = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrEmpty($Dosya)) {
    $Dosya = Join-Path $kok "docs\RAPOR\N-Emek-Teknik-Rapor.docx"
}
if (-not (Test-Path $Dosya)) {
    Write-Output "bulunamadi: $Dosya"
    Write-Output "  once: .venv\Scripts\python.exe scripts\rapor_docx.py"
    exit 2
}
$Dosya = (Resolve-Path $Dosya).Path

$SAYFA_SINIRI = 30

# Dosya baskasinda acikken `Documents.Open` bir "kullanimda" iletisim
# kutusu acar; bu betik etkilesimsiz kostugu icin orada asili kalir -
# bir kez oldu ve iki oksuz WINWORD surecinden anlasildi. Kilidi
# onceden yoklayip anlasilir bir hatayla durmak, zaman asimini
# beklemekten iyi.
try {
    $akis = [System.IO.File]::Open($Dosya, "Open", "ReadWrite", "None")
    $akis.Close()
}
catch {
    Write-Output "dosya kilitli: $Dosya"
    Write-Output "  Word'de acik olabilir; kapatin."
    Write-Output "  Gorunmez kalmis otomasyon sureci varsa: Get-Process WINWORD"
    exit 2
}

$word = $null
$belge = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    # Word bir sey soramaz: bu betik etkilesimsiz kosuyor ve bir iletisim
    # kutusu acilirsa surec zaman asimina kadar asili kalir.
    $word.DisplayAlerts = 0

    $belge = $word.Documents.Open($Dosya, $false, $false)

    # Icindekiler once guncellenir; sayfa sayisi ondan sonra okunur,
    # cunku icindekiler kendisi bir sayfa buyuyebilir.
    foreach ($icindekiler in $belge.TablesOfContents) { $icindekiler.Update() }
    $belge.Repaginate()

    # wdStatisticPages = 2, wdStatisticWords = 0
    $sayfa = $belge.ComputeStatistics(2, $false)
    $kelime = $belge.ComputeStatistics(0, $false)

    Write-Output "sayfa   : $sayfa / $SAYFA_SINIRI"
    Write-Output "kelime  : $kelime"

    # Yazi tipi ve punto denetimi bilincli olarak burada *degil*:
    # COM uzerinden paragraf paragraf `Range.Font` okumak dakikalar
    # suruyor ve betigi asili birakti. Ayni denetim `rapor_denetimi.py`
    # icinde dosyanin XML'i uzerinden aninda yapiliyor.
    $belge.Save()

    if ($Pdf) {
        $pdfYolu = [System.IO.Path]::ChangeExtension($Dosya, ".pdf")
        # wdExportFormatPDF = 17
        $belge.ExportAsFixedFormat($pdfYolu, 17)
        Write-Output "pdf     : $pdfYolu"
    }

    if ($sayfa -gt $SAYFA_SINIRI) {
        Write-Output ""
        Write-Output "SAYFA SINIRI ASILDI: $sayfa > $SAYFA_SINIRI"
        exit 1
    }
}
finally {
    # Temizlik olcumu gizlememeli. PDF disa aktarimindan sonra Word
    # bagi kendiliginden kopariyor (RPC_E_DISCONNECTED); o hata sayfa
    # sayisini gecersiz kilmiyor ama betigi kirmizi gosteriyordu.
    try { if ($null -ne $belge) { $belge.Close(0) } } catch {}
    try { if ($null -ne $word) { $word.Quit() } } catch {}
    try {
        if ($null -ne $word) {
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
        }
    } catch {}
}
