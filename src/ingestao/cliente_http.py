"""
Cliente HTTP minimo com retry e backoff exponencial.

As APIs do Banco Central sao publicas, sem chave, mas instaveis: o Olinda devolve
HTTP 500 de vez em quando e pode demorar. Em vez de falhar na primeira, tentamos
de novo esperando 2s, 4s, 8s... Erros permanentes (400, 404, 406) nao sao
repetidos, porque repetir nao resolve.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from urllib.parse import quote

import requests

log = logging.getLogger(__name__)

CODIGOS_TEMPORARIOS = {429, 500, 502, 503, 504}


def montar_url_odata(url_base: str, parametros: dict) -> str:
    """
    Monta a URL de uma consulta OData do Olinda.

    O requests codificaria '@' como %40 e espaco como '+', e o Olinda responde 400.
    Por isso montamos a query na mao: '@', '$' e aspas simples ficam como estao e o
    espaco vira %20.
    """
    partes = []
    for chave, valor in parametros.items():
        chave_codificada = quote(str(chave), safe="@$")
        valor_codificado = quote(str(valor), safe="'")
        partes.append(f"{chave_codificada}={valor_codificado}")
    return url_base + "?" + "&".join(partes)


class ErroTemporario(Exception):
    """Falha que vale a pena tentar de novo."""


def obter_json(
    url: str,
    parametros: dict | None = None,
    tentativas: int = 5,
    espera_inicial: float = 2.0,
    timeout: int = 180,
) -> dict | list:
    """Faz GET e devolve o JSON. Repete em erros temporarios com backoff exponencial."""
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(
                url,
                params=parametros,
                timeout=timeout,
                headers={"Accept": "application/json", "User-Agent": "pix-macro-lakehouse/0.1"},
            )
            if resposta.status_code in CODIGOS_TEMPORARIOS:
                raise ErroTemporario(f"HTTP {resposta.status_code}: {resposta.text[:200]}")
            resposta.raise_for_status()
            return resposta.json()
        except (requests.Timeout, requests.ConnectionError, ErroTemporario, ValueError) as erro:
            ultimo_erro = erro
            if tentativa == tentativas:
                break
            espera = espera_inicial * (2 ** (tentativa - 1))
            log.warning(
                "tentativa %d/%d falhou (%s); aguardando %.0fs", tentativa, tentativas, erro, espera
            )
            time.sleep(espera)
    raise RuntimeError(f"falha definitiva em {url} apos {tentativas} tentativas: {ultimo_erro}")


def montar_envelope(fonte: str, url: str, parametros: dict, dados: list) -> dict:
    """
    Embala os registros com os metadados de ingestao. E este envelope que vai para o
    arquivo JSON (modo volume) ou direto para o bronze (modo api). Assim o bronze
    sabe sempre de onde, quando e com quais parametros cada linha veio.
    """
    return {
        "metadados": {
            "fonte": fonte,
            "url": url,
            "parametros": {chave: str(valor) for chave, valor in parametros.items()},
            "baixado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "quantidade_registros": len(dados),
        },
        "dados": dados,
    }
