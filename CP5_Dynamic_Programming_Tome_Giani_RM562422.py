"""Checkpoint 5 - Programacao Dinamica em Strings.

Execute este arquivo na mesma pasta de transcricoes_atividade.csv e catalogo.csv.
Ele gera todas as saidas exigidas pelo checkpoint, sem bibliotecas de similaridade.
"""

from collections import Counter
from pathlib import Path
import re

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_TRANSCRICOES = BASE_DIR / "transcricoes_atividade.csv"
ARQUIVO_CATALOGO = BASE_DIR / "catalogo.csv"
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+")
MINIMO_APROXIMACAO = 4


def limpar_texto(texto):
    """Normaliza texto para comparacao: minusculas, sem pontuacao e espacos unicos."""
    texto = "" if pd.isna(texto) else str(texto)
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-zà-öø-ÿ]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def comparar_exato(a, b):
    """Compara duas entradas depois da mesma limpeza controlada."""
    return limpar_texto(a) == limpar_texto(b)


def matriz_distancia(a, b):
    """Constroi a matriz bottom-up da distancia de edicao de Levenshtein."""
    a = limpar_texto(a)
    b = limpar_texto(b)
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                remover = dp[i - 1][j]
                inserir = dp[i][j - 1]
                substituir = dp[i - 1][j - 1]
                dp[i][j] = 1 + min(remover, inserir, substituir)
    return dp


def distancia_edicao(a, b):
    """Retorna a distancia final da matriz de programacao dinamica."""
    return matriz_distancia(a, b)[-1][-1]


def gerar_frequencia(df):
    """Conta palavras do corpus para documentar a construcao do catalogo."""
    contador = Counter()
    for texto in df["texto"].astype(str):
        contador.update(
            palavra.lower()
            for palavra in TOKEN_RE.findall(texto)
            if len(palavra) >= MINIMO_APROXIMACAO
        )
    return pd.DataFrame(
        contador.most_common(), columns=["palavra", "frequencia"]
    ), contador


def carregar_entradas():
    """Le e valida corpus e catalogo, preservando os campos do enunciado."""
    df = pd.read_csv(ARQUIVO_TRANSCRICOES)
    colunas_esperadas = {"id", "meeting_id", "locutor", "texto"}
    if not colunas_esperadas.issubset(df.columns):
        raise ValueError("CSV de transcricoes nao possui as colunas obrigatorias.")
    if len(df) != 420:
        raise ValueError(f"Esperados 420 registros; encontrados {len(df)}.")

    catalogo_df = pd.read_csv(ARQUIVO_CATALOGO)
    if "termo" not in catalogo_df.columns:
        raise ValueError("catalogo.csv precisa ter a coluna termo.")
    catalogo = [limpar_texto(t) for t in catalogo_df["termo"].dropna()]
    catalogo = [t for t in catalogo if t]
    if not 80 <= len(catalogo) <= 150:
        raise ValueError("O catalogo deve ter entre 80 e 150 termos.")
    if len(set(catalogo)) != len(catalogo):
        raise ValueError("O catalogo contem termos duplicados.")
    return df, catalogo, catalogo_df


def classificar_termo(palavra, catalogo, limite):
    """Faz a triagem EXATO -> PENDENTE_DP e aplica a regra de aceitacao.

    Retorno: candidato, distancia, status, candidatos_empate.
    Status possiveis: EXATO, CORRIGIDO, AMBIGUO e MANTIDO.
    """
    normalizada = limpar_texto(palavra)
    catalogo_set = set(catalogo)

    # Triagem obrigatoria: nao chama DP quando existe igualdade exata.
    if normalizada in catalogo_set:
        return normalizada, 0, "EXATO", [normalizada]

    if len(normalizada) < MINIMO_APROXIMACAO:
        return palavra, None, "MANTIDO", []

    distancias = [(termo, distancia_edicao(normalizada, termo)) for termo in catalogo]
    menor = min(distancia for _, distancia in distancias)
    melhores = [termo for termo, distancia in distancias if distancia == menor]

    if menor <= limite and len(melhores) == 1:
        return melhores[0], menor, "CORRIGIDO", melhores
    if menor <= limite and len(melhores) > 1:
        return palavra, menor, "AMBIGUO", melhores
    return palavra, menor, "MANTIDO", melhores


def processar_texto(texto, catalogo, limite):
    """Processa uma frase sem perder seus espacos e sinais de pontuacao."""
    contagem = Counter()
    correcoes = []

    def substituir(match):
        original = match.group(0)
        candidato, distancia, status, empate = classificar_termo(
            original, catalogo, limite
        )
        contagem[status] += 1
        contagem["termos_analisados"] += 1
        if status == "CORRIGIDO":
            correcoes.append(
                {
                    "original": original,
                    "candidato": candidato,
                    "distancia": distancia,
                    "status": status,
                }
            )
        return candidato

    tratado = TOKEN_RE.sub(substituir, str(texto))
    return tratado, contagem, correcoes


def processar_corpus(df, catalogo, limite):
    """Executa o pipeline sobre os 420 registros e mantem rastreabilidade."""
    resultado = df.copy()
    textos_tratados, logs = [], []
    totais = Counter()
    por_status = {"EXATO": [], "CORRIGIDO": [], "AMBIGUO": [], "MANTIDO": []}

    for indice, linha in resultado.iterrows():
        tratado, contagem, correcoes = processar_texto(linha["texto"], catalogo, limite)
        textos_tratados.append(tratado)
        totais.update(contagem)
        for status in por_status:
            por_status[status].append(contagem[status])
        for correcao in correcoes:
            logs.append(
                {
                    "linha_csv": indice,
                    "id": linha["id"],
                    "meeting_id": linha["meeting_id"],
                    "locutor": linha["locutor"],
                    "original": correcao["original"],
                    "candidato": correcao["candidato"],
                    "distancia": correcao["distancia"],
                    "limite": limite,
                    "status": correcao["status"],
                }
            )

    resultado = resultado.rename(columns={"texto": "texto_original"})
    resultado["texto_tratado"] = textos_tratados
    for status, valores in por_status.items():
        resultado[f"qtd_{status.lower()}"] = valores
    correcoes_df = pd.DataFrame(
        logs,
        columns=[
            "linha_csv", "id", "meeting_id", "locutor", "original", "candidato",
            "distancia", "limite", "status",
        ],
    )
    return resultado, correcoes_df, totais


def resumo_estatistico(totais, total_registros, tamanho_catalogo, limite):
    linhas = [
        ("limite_distancia", limite),
        ("registros_processados", total_registros),
        ("termos_analisados", totais["termos_analisados"]),
        ("EXATO", totais["EXATO"]),
        ("CORRIGIDO", totais["CORRIGIDO"]),
        ("AMBIGUO", totais["AMBIGUO"]),
        ("MANTIDO", totais["MANTIDO"]),
        ("percentual_correcoes_automaticas", round(
            100 * totais["CORRIGIDO"] / totais["termos_analisados"], 2
        )),
        ("termos_no_catalogo", tamanho_catalogo),
    ]
    return pd.DataFrame(linhas, columns=["metrica", "valor"])


def executar_limite(df, catalogo, limite):
    resultado, correcoes, totais = processar_corpus(df, catalogo, limite)
    resumo = resumo_estatistico(totais, len(resultado), len(catalogo), limite)
    resultado.to_csv(
        BASE_DIR / f"transcricoes_processadas_L{limite}.csv",
        index=False, encoding="utf-8-sig",
    )
    correcoes.to_csv(
        BASE_DIR / f"correcoes_realizadas_L{limite}.csv",
        index=False, encoding="utf-8-sig",
    )
    resumo.to_csv(
        BASE_DIR / f"estatisticas_resumo_L{limite}.csv",
        index=False, encoding="utf-8-sig",
    )
    return resultado, correcoes, resumo


def executar_testes_minimos():
    """Testes exigidos no enunciado antes do processamento integral."""
    assert limpar_texto(" TOTOS ") == "totos"
    assert comparar_exato("TOTVS", " totvs ") is True
    assert comparar_exato("Totos", "totvs") is False
    assert distancia_edicao("protheu", "protheus") == 1
    assert distancia_edicao("totvss", "totvs") == 1
    matriz = matriz_distancia("totos", "totvs")
    assert len(matriz) == 6 and len(matriz[0]) == 6
    assert matriz[0] == [0, 1, 2, 3, 4, 5]
    _, distancia, status, _ = classificar_termo("cana", ["casa", "cama"], 1)
    assert distancia == 1 and status == "AMBIGUO"
    print("Todos os testes minimos passaram.")


def main():
    executar_testes_minimos()
    df, catalogo, _ = carregar_entradas()
    frequencia_df, _ = gerar_frequencia(df)
    frequencia_df.to_csv(BASE_DIR / "frequencia_palavras.csv", index=False, encoding="utf-8-sig")

    resultado_l1, correcoes_l1, resumo_l1 = executar_limite(df, catalogo, 1)
    resultado_l2, correcoes_l2, resumo_l2 = executar_limite(df, catalogo, 2)

    comparacao = resumo_l1.set_index("metrica").join(
        resumo_l2.set_index("metrica"), lsuffix="_L1", rsuffix="_L2"
    )
    comparacao["diferenca_L2_menos_L1"] = (
        comparacao["valor_L2"] - comparacao["valor_L1"]
    )
    comparacao.loc["registros_alterados"] = [
        int((resultado_l1["qtd_corrigido"] > 0).sum()),
        int((resultado_l2["qtd_corrigido"] > 0).sum()),
        int((resultado_l2["qtd_corrigido"] > 0).sum() - (resultado_l1["qtd_corrigido"] > 0).sum()),
    ]
    comparacao.reset_index(names="metrica").to_csv(
        BASE_DIR / "estatisticas_resumo.csv", index=False, encoding="utf-8-sig"
    )

    print(f"Registros processados: {len(df)}")
    print(f"Catalogo validado: {len(catalogo)} termos")
    print("Saidas geradas para L1 e L2.")
    print("Correcoes L1:", len(correcoes_l1), "| Correcoes L2:", len(correcoes_l2))


if __name__ == "__main__":
    main()
