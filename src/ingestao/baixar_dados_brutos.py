"""
Script local de ingestao: baixa as fontes do BCB para data/raw/ como JSON.

Uso (na raiz do repositorio):
    python -m src.ingestao.baixar_dados_brutos                       # tudo
    python -m src.ingestao.baixar_dados_brutos --fontes selic_meta ipca
    python -m src.ingestao.baixar_dados_brutos --fontes pix_estatisticas --mes-inicio 202401 --mes-fim 202403
    python -m src.ingestao.baixar_dados_brutos --somente-faltantes   # pula meses ja baixados

Cada arquivo e um envelope {"metadados": {...}, "dados": [...]} (ver cliente_http.montar_envelope).
Depois, src/ingestao/subir_volume.py copia a pasta para o Volume do Unity Catalog.
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

from config.configuracoes import (
    FONTES,
    MESES_RECARGA,
    PASTA_DADOS_BRUTOS,
    PIX_MES_INICIO,
    SGS_DATA_INICIO,
    SGS_JANELA_ANOS,
)
from src.ingestao import cooperativas, olinda_pix, sgs
from src.transformacoes.calendario import data_para_ano_mes, janelas_sgs, meses_entre, somar_meses

log = logging.getLogger("ingestao")


def salvar_envelope(envelope: dict, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(envelope, arquivo, ensure_ascii=False)
    log.info("salvo %s (%d registros)", caminho, envelope["metadados"]["quantidade_registros"])


def baixar_fonte_pix(
    fonte: str, pasta: Path, mes_inicio: int, mes_fim: int, somente_faltantes: bool
) -> None:
    primeiro_mes_recarga = somar_meses(mes_fim, -(MESES_RECARGA - 1))
    for ano_mes in meses_entre(mes_inicio, mes_fim):
        caminho = pasta / fonte / f"{fonte}_{ano_mes}.json"
        # Meses antigos podem ser pulados; os ultimos MESES_RECARGA sempre sao rebaixados,
        # porque o BCB revisa dados recentes.
        if somente_faltantes and caminho.exists() and ano_mes < primeiro_mes_recarga:
            continue
        salvar_envelope(olinda_pix.baixar_mes(fonte, ano_mes), caminho)


def baixar_fonte_sgs(fonte: str, pasta: Path, data_fim: date) -> None:
    for inicio, fim in janelas_sgs(SGS_DATA_INICIO, data_fim, SGS_JANELA_ANOS):
        caminho = pasta / fonte / f"{fonte}_{inicio.isoformat()}_{fim.isoformat()}.json"
        salvar_envelope(sgs.baixar_janela(fonte, inicio, fim), caminho)


def baixar_fonte_cooperativas(pasta: Path, hoje: date) -> None:
    caminho = pasta / "cooperativas" / f"cooperativas_{hoje.isoformat()}.json"
    salvar_envelope(cooperativas.baixar_cooperativas(), caminho)


def main(argumentos: list[str] | None = None) -> None:
    hoje = date.today()
    parser = argparse.ArgumentParser(description="Baixa dados abertos do BCB para data/raw/.")
    parser.add_argument("--fontes", nargs="+", choices=sorted(FONTES), default=sorted(FONTES))
    parser.add_argument("--mes-inicio", type=int, default=PIX_MES_INICIO, help="AAAAMM (fontes Pix)")
    parser.add_argument(
        "--mes-fim", type=int, default=data_para_ano_mes(hoje), help="AAAAMM (fontes Pix)"
    )
    parser.add_argument("--pasta", default=PASTA_DADOS_BRUTOS)
    parser.add_argument("--somente-faltantes", action="store_true")
    args = parser.parse_args(argumentos)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    pasta = Path(args.pasta)

    for fonte in args.fontes:
        tipo = FONTES[fonte]["tipo"]
        log.info("== fonte %s (%s) ==", fonte, tipo)
        if tipo == "olinda_pix":
            baixar_fonte_pix(fonte, pasta, args.mes_inicio, args.mes_fim, args.somente_faltantes)
        elif tipo == "sgs":
            baixar_fonte_sgs(fonte, pasta, hoje)
        elif tipo == "olinda_instituicoes":
            baixar_fonte_cooperativas(pasta, hoje)


if __name__ == "__main__":
    main()
