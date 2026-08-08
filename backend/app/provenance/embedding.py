"""CLIP tabanli gorsel gomme (embedding) uretimi.

Algisal hash'in coktugu yerde devreye girer: agir duzenleme, kolaj,
stil transferi, yeniden cizim. Semantik/yapisal benzerligi yakalar ama
tek basina "ayni icerik" kaniti sayilmaz - koken kurtarma hattinda
aday uretici olarak kullanilir, karari geometri asamasi verir.

Model varsayilan olarak ViT-B/32'dir (512 boyut, 4 GB VRAM'e rahat
sigar). `NEMEK_CLIP_MODEL` ortam degiskeniyle degistirilebilir.
"""

from __future__ import annotations

import os
from functools import lru_cache

import numpy as np
import torch
from PIL import Image

MODEL_NAME = os.getenv("NEMEK_CLIP_MODEL", "ViT-B-32")
PRETRAINED = os.getenv("NEMEK_CLIP_PRETRAINED", "laion2b_s34b_b79k")
EMBEDDING_DIM = 512


def pick_device() -> str:
    if os.getenv("NEMEK_FORCE_CPU") == "1":
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def _load():
    """Modeli bir kez yukler. Ilk cagri model indirmesi nedeniyle yavastir."""
    import open_clip

    device = pick_device()
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME, pretrained=PRETRAINED, device=device
    )
    model.eval()
    return model, preprocess, device


def embed(images: list[Image.Image], batch_size: int = 16) -> np.ndarray:
    """Gorselleri L2-normalize edilmis vektorlere cevirir.

    Returns:
        (N, EMBEDDING_DIM) float32 dizi. Kosinus benzerligi = ic carpim.
    """
    if not images:
        return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

    model, preprocess, device = _load()
    out: list[np.ndarray] = []
    autocast = torch.autocast(device_type="cuda", dtype=torch.float16) if device == "cuda" else None

    for start in range(0, len(images), batch_size):
        chunk = images[start : start + batch_size]
        tensor = torch.stack([preprocess(img.convert("RGB")) for img in chunk]).to(device)
        with torch.no_grad():
            if autocast is not None:
                with autocast:
                    feats = model.encode_image(tensor)
            else:
                feats = model.encode_image(tensor)
        feats = feats.float()
        feats /= feats.norm(dim=-1, keepdim=True)
        out.append(feats.cpu().numpy().astype(np.float32))

    return np.vstack(out)


def embed_one(image: Image.Image) -> np.ndarray:
    return embed([image])[0]


def clip_confidence(similarity: float) -> float:
    """Kosinus benzerligini guven skoruna cevirir.

    CLIP benzerligi "ayni sahne" ile "ayni icerik"i ayirmaz; bu yuzden
    ust sinir bilincli olarak dusuk tutulmustur (0.75). Kesin karar
    geometri asamasindan gelir.
    """
    if similarity < 0.75:
        return 0.0
    # 0.75 -> 0.30, 1.00 -> 0.75
    return round(min(0.75, 0.30 + (similarity - 0.75) * 1.8), 4)
