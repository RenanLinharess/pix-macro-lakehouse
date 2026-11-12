"""
Gera os arquivos sql/ddl/*.sql a partir da especificacao em src/catalogo/tabelas.py.

Uso: python -m src.catalogo.gerar_ddl

Os arquivos gerados servem para leitura e revisao (e podem ser executados no editor SQL).
O notebook 00_preparar_ambiente usa a especificacao diretamente, sem depender dos arquivos.
"""
from __future__ import annotations

from pathlib import Path

from src.catalogo.tabelas import ddl_comentarios, ddl_criar_tabela, todas_as_tabelas

PASTA_DDL = Path("sql/ddl")


def main() -> None:
    PASTA_DDL.mkdir(parents=True, exist_ok=True)
    for camada, chave in todas_as_tabelas():
        caminho = PASTA_DDL / f"{camada}_{chave}.sql"
        conteudo = "-- Gerado por src/catalogo/gerar_ddl.py a partir de src/catalogo/tabelas.py. Nao edite a mao.\n"
        conteudo += ddl_criar_tabela(camada, chave) + ";\n\n"
        conteudo += "-- Comentarios reaplicados a cada execucao do pipeline:\n"
        conteudo += ";\n".join(ddl_comentarios(camada, chave)) + ";\n"
        caminho.write_text(conteudo, encoding="utf-8")
        print("gerado", caminho)


if __name__ == "__main__":
    main()
