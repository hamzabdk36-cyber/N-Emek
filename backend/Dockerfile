# N-Emek backend
#
# PyTorch bilerek CPU surumu: juri makinesinde NVIDIA suruculeri ve
# nvidia-container-toolkit olmayabilir ve kurulumun tek komutla calismasi
# GPU hizindan onemli. GPU'lu makinede yerel kurulum (bkz. README) CUDA
# kullanir; Docker'da GPU icin compose dosyasindaki nota bakin.

FROM python:3.13-slim

# OpenCV'nin paylasilan kutuphaneleri. `opencv-contrib-python` (headless
# olmayan surum) libGL ve libglib istiyor; bagimliligi degistirmek yerine
# imaja bu iki kutuphaneyi koyuyoruz ki yerel kurulumla ayni paket kalsin.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# SIRA ONEMLI: torch once ve CPU indeksinden kurulur.
#
# Ters sirada calismiyor - ilk denemede oyle yazilmisti ve gercek build
# hatayi gosterdi: `requirements.txt` icindeki `open_clip_torch`, torch'u
# bagimlilik olarak cekiyor ve pip bunu varsayilan PyPI'den, yani CUDA'li
# halinden aliyor. Arkasindan gelen CPU komutu "zaten kurulu" deyip
# geciyor. Sonuc: 750 MB'lik nvidia_* paketleri (cudnn, nccl, cusparselt)
# ve ~8 GB'lik bir imaj - hem de GPU'su olmayan makineler icin.
#
# Torch once kurulunca `requirements.txt` onu karsilanmis buluyor ve
# CUDA surumune hic dokunmuyor.
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir torch torchvision \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY scripts/ scripts/
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# CLIP modeli ilk caliştirmada iniyor; onbellek birim (volume) olarak
# baglanmazsa her kapsayici yeniden indirir.
ENV HF_HOME=/cache/huggingface \
    PYTHONUNBUFFERED=1 \
    NEMEK_DATA_DIR=/app/data \
    NEMEK_UPLOAD_DIR=/app/data/uploads \
    NEMEK_INDEX_DIR=/app/data/index \
    NEMEK_DATABASE_URL=sqlite:////app/data/nemek.db

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
