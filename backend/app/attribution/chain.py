"""Atif zincirinin veritabanindan cikarilmasi.

`contribution.compute_shares` saf bir fonksiyondur ve zinciri hazir
bekler. Bu modul o zinciri kurar: yapraktan yukari dogru yurur, cok
adimli kapsamayi hesaplar ve her kaynak icin tek bir `ChainNode` uretir.

Cok adimli kapsama
------------------
Geometri yalnizca *dogrudan* cift icin olcum yapar (turev <- kaynak).
Buyukbaba icerigin yapraktaki payini ayrica olcmek yerine zincir boyunca
carparak turetiyoruz:

    kapsama(buyukbaba, yaprak) = kapsama(baba, yaprak) x kapsama(buyukbaba, baba)

Gerekce: baba icerigin yaprakta gorunen kismi, babanin kendi icindeki
buyukbaba oranini da ayni olcude tasir. Bu bir yaklasimdir - yaprakta
gorunen bolge tam olarak babanin buyukbabadan gelen bolgesine denk
gelmeyebilir. Alternatif (her ata cifti icin ayri geometri kosmak)
zincir uzadikca karesel maliyet getirir ve dogrudan olcum icin kaynak
gorselin hala erisilebilir olmasini gerektirir.

Ayni ataya birden fazla yol varsa (or. bir kolajda ayni kaynak iki kez
kullanilmis) en guclu yol secilir, toplanmaz. Toplamak, ayni emegi iki
kez odullendirir.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.attribution.contribution import ChainNode
from app.core.config import get_settings
from app.models.entities import AttributionEdge, Content, LinkStatus, User


def _usable_edges(session: Session, child_id: str) -> list[AttributionEdge]:
    stmt = select(AttributionEdge).where(
        AttributionEdge.child_id == child_id,
        AttributionEdge.status.in_([LinkStatus.PROPOSED, LinkStatus.CONFIRMED]),
    )
    return list(session.scalars(stmt))


def _collect_subgraph(
    session: Session, leaf_id: str, max_depth: int
) -> dict[str, list[AttributionEdge]]:
    """Yapraktan yukari erisilebilen tum baglari toplar (child_id -> kenarlar)."""
    graph: dict[str, list[AttributionEdge]] = {}
    frontier = [leaf_id]
    depth = 0
    while frontier and depth <= max_depth:
        nxt: list[str] = []
        for node_id in frontier:
            if node_id in graph:
                continue
            edges = _usable_edges(session, node_id)
            graph[node_id] = edges
            nxt.extend(e.parent_id for e in edges)
        frontier = nxt
        depth += 1
    return graph


def _redundant_edges(graph: dict[str, list[AttributionEdge]]) -> set[str]:
    """Gecisli indirgeme: dolayli yolu da olan dogrudan baglari isaretler.

    Neden gerekli
    -------------
    Geometri asamasi, Ceyda'nin icerigindeki Ayse'yi de bulur - cunku
    Ayse'nin pikselleri Burak'in remixi araciligiyla oraya ulasmistir.
    Bu, Ayse -> Ceyda dogrudan bagini uretir. Ama gercek turetme tarihi
    Ayse -> Burak -> Ceyda'dir ve iki bag *ayni pikselleri* temsil eder.
    Ikisini birden saymak, ayni emegi iki kez odullendirir; olculen
    kapsamalarin toplami %100'u asar.

    Cozum, klasik gecisli indirgeme: P'den C'ye uzunlugu 2 veya daha
    fazla bir yol varsa, dogrudan P -> C bagi pay hesabindan dusulur.
    Bag veritabaninda kanit olarak kalir; yalnizca zincir yurumesinde
    dikkate alinmaz, cunku katkisi zaten dolayli yol uzerinden sayilir.
    """
    # parent -> child yonlu komsuluk (turetme yonu)
    children: dict[str, set[str]] = {}
    for child_id, edges in graph.items():
        for edge in edges:
            children.setdefault(edge.parent_id, set()).add(child_id)

    def reachable_in_two_or_more(start: str, target: str) -> bool:
        """start'tan target'a en az iki adimda ulasilabiliyor mu."""
        # Ilk adimi ayri at: dogrudan bagi yol olarak saymamak icin.
        frontier = {c for c in children.get(start, set()) if c != target}
        seen = set(frontier)
        while frontier:
            nxt: set[str] = set()
            for node in frontier:
                for succ in children.get(node, set()):
                    if succ == target:
                        return True
                    if succ not in seen:
                        seen.add(succ)
                        nxt.add(succ)
            frontier = nxt
        return False

    redundant: set[str] = set()
    for child_id, edges in graph.items():
        for edge in edges:
            if reachable_in_two_or_more(edge.parent_id, child_id):
                redundant.add(edge.id)
    return redundant


def reduced_subgraph(session: Session, leaf_id: str) -> dict[str, list[AttributionEdge]]:
    """Yapraga baglanan alt grafik, gecisli indirgeme uygulanmis hali.

    `build_chain` zaten bunu kendi icinde yapiyor; disari acmamizin
    sebebi zincir gorunumunun ayni kenar kumesini gormesi. Aksi halde
    ekranda Ayse -> Ceyda dogrudan bagi da cizilir ve izleyici
    kapsamalari toplayip %100'u astigini gorur - oysa o bag pay
    hesabina hic girmemistir.
    """
    settings = get_settings()
    graph = _collect_subgraph(session, leaf_id, settings.max_chain_depth)
    redundant = _redundant_edges(graph)
    return {
        child_id: [e for e in edges if e.id not in redundant]
        for child_id, edges in graph.items()
    }


def build_chain(session: Session, content_id: str) -> list[ChainNode]:
    """Yapraktan yukari tum atalari toplar."""
    settings = get_settings()
    # content_id -> en guclu yolun verileri
    best: dict[str, dict] = {}

    graph = _collect_subgraph(session, content_id, settings.max_chain_depth)
    redundant = _redundant_edges(graph)

    def walk(
        current_id: str,
        depth: int,
        coverage: float,
        confidence: float,
        path_verified: bool,
        seen: set[str],
    ):
        if depth > settings.max_chain_depth:
            return
        for edge in graph.get(current_id, []):
            if edge.id in redundant:
                # Ayni katki dolayli yol uzerinden zaten sayilacak.
                continue
            parent_id = edge.parent_id
            if parent_id in seen:
                # Dongu koruma: bir icerik kendi atasi olamaz.
                continue

            # Geometri olcemediyse kapsama None kalir; ihtiyatli varsayim
            # contribution katmaninda uygulanir, burada isaretlenir.
            step_verified = edge.visual_coverage is not None
            step_coverage = (
                edge.visual_coverage if step_verified else settings.unverified_coverage
            )
            eff_coverage = coverage * step_coverage
            eff_confidence = confidence * edge.confidence
            # Zincirin tamami olculmediyse sonuc olculmus sayilmaz:
            # tek bir dogrulanmamis halka tum yolu belirsiz yapar.
            eff_verified = path_verified and step_verified

            weight = eff_coverage * eff_confidence
            previous = best.get(parent_id)
            if previous is None or weight > previous["weight"]:
                best[parent_id] = {
                    "weight": weight,
                    "depth": depth,
                    "coverage": eff_coverage,
                    "confidence": eff_confidence,
                    "verified": eff_verified,
                    "stage": edge.stage.value,
                    "edge_id": edge.id,
                }

            walk(
                parent_id,
                depth + 1,
                eff_coverage,
                eff_confidence,
                eff_verified,
                seen | {parent_id},
            )

    walk(content_id, 1, 1.0, 1.0, True, {content_id})

    # --- Ozel (exclusive) kapsama -----------------------------------------
    # Buraya kadar hesaplanan kapsama *toplam* kapsamadir: bir kaynagin
    # yaprakta gorunen tum pikselleri. Ama bu sayilar ic ice gecmistir -
    # Burak'in yapraktaki %97'si, Ayse'nin %85'ini de icerir. Ikisini
    # toplamak ayni pikseli iki kez odullendirir.
    #
    # Her dugume yalnizca *kendi kattigi* pikselleri yaziyoruz:
    #
    #     ozel(A) = toplam(A) - toplam(A'nin zincirdeki dogrudan kaynaklari)
    #
    # Yaprak icin toplam 1.0 kabul edilir. Boylece ozel kapsamalar
    # gorselin tam bir bolutlemesidir ve dogal olarak 1.0'a toplanir;
    # pay hesabi normalizasyona degil olcume dayanir.
    totals = {pid: data["coverage"] for pid, data in best.items()}
    totals[content_id] = 1.0

    direct_parents: dict[str, list[str]] = {}
    for child, edges in graph.items():
        if child not in totals:
            continue
        direct_parents[child] = [
            e.parent_id
            for e in edges
            if e.id not in redundant and e.parent_id in totals
        ]

    exclusive: dict[str, float] = {}
    for node_id, total in totals.items():
        consumed = sum(totals[p] for p in direct_parents.get(node_id, []))
        exclusive[node_id] = max(0.0, total - consumed)

    nodes: list[ChainNode] = []
    for parent_id, data in best.items():
        content = session.get(Content, parent_id)
        if content is None:
            continue
        owner = session.get(User, content.owner_id)
        nodes.append(
            ChainNode(
                content_id=parent_id,
                owner_id=content.owner_id,
                owner_name=owner.display_name if owner else "bilinmiyor",
                depth=data["depth"],
                coverage=exclusive[parent_id],
                total_coverage=data["coverage"],
                confidence=data["confidence"],
                geometry_verified=data["verified"],
                min_source_share=content.min_source_share,
                stage=data["stage"],
            )
        )

    # Cok kucuk katkilari zincirden dusur: gurultu, Emek Karti'ni
    # okunmaz hale getirir ve zaten odeme esiginin altinda kalir.
    nodes = [n for n in nodes if n.coverage >= settings.min_coverage_for_share]
    nodes.sort(key=lambda n: (n.depth, -n.coverage))
    return nodes


def descendants(session: Session, content_id: str) -> list[AttributionEdge]:
    """Bu icerigi kaynak alan turevler (zincir gorunumu icin)."""
    stmt = select(AttributionEdge).where(AttributionEdge.parent_id == content_id)
    return list(session.scalars(stmt))
