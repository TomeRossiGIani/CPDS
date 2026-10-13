"""Gera a versao .ipynb a partir do script principal do checkpoint."""

import json
from pathlib import Path


PASTA = Path(__file__).resolve().parent
fonte = (PASTA / "CP5_Dynamic_Programming_Tome_Giani_RM562422.py").read_text(
    encoding="utf-8"
)
fonte = fonte.replace(
    "BASE_DIR = Path(__file__).resolve().parent", "BASE_DIR = Path.cwd()"
)

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Checkpoint 5 Programacao Dinamica em Strings\n",
                "\n",
                "**Tomé Rossi Giani - RM 562422**\n",
                "\n",
                "Este notebook processa o corpus de 420 transcricoes, gera frequencia, "
                "aplica a distancia de edicao implementada com Programacao Dinamica e "
                "compara os limites 1 e 2.",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Execucao completa\n",
                "\n",
                "Deixe os arquivos CSV na mesma pasta do notebook e execute a celula abaixo. "
                "Os testes minimos sao executados antes do processamento integral.",
            ],
        },
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": fonte.splitlines(keepends=True)},
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

(PASTA / "CP5_Dynamic_Programming_Tome_Giani_RM562422.ipynb").write_text(
    json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8"
)
