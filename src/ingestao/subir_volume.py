"""
Copia data/raw/ para o Volume do Unity Catalog usando a CLI do Databricks.

Uso:
    python -m src.ingestao.subir_volume            # usa o perfil de DATABRICKS_CONFIG_PROFILE (.env)
    python -m src.ingestao.subir_volume --perfil outro-perfil

Exige a CLI autenticada (databricks auth login). O token fica no perfil da CLI, fora do repo.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

from config.configuracoes import CAMINHO_VOLUME_BRUTO, PASTA_DADOS_BRUTOS


def main(argumentos: list[str] | None = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Sobe data/raw/ para o Volume do Unity Catalog.")
    parser.add_argument("--perfil", default=os.getenv("DATABRICKS_CONFIG_PROFILE", "DEFAULT"))
    parser.add_argument("--pasta", default=PASTA_DADOS_BRUTOS)
    args = parser.parse_args(argumentos)

    comando = [
        "databricks", "fs", "cp", "--recursive", "--overwrite",
        args.pasta, f"dbfs:{CAMINHO_VOLUME_BRUTO}",
        "--profile", args.perfil,
    ]
    print("executando:", " ".join(comando))
    resultado = subprocess.run(comando)
    sys.exit(resultado.returncode)


if __name__ == "__main__":
    main()
