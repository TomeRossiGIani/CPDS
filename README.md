# Checkpoint 5 Dynamic Programming em Strings

**Aluno:** Tome Rossi Giani - **RM:** 562422  
**Disciplina:** Dynamic Programming - TOTVS

## Como executar

Mantenha `transcricoes_atividade.csv` e `catalogo.csv` na mesma pasta do arquivo `CP5_Dynamic_Programming_Tome_Giani_RM562422.py`. Em seguida, execute:

```bash
python CP5_Dynamic_Programming_Tome_Giani_RM562422.py
```

O projeto pode ser aberto no Colab pelo notebook `CP5_Dynamic_Programming_Tome_Giani_RM562422.ipynb`. Todos os CSVs de saida sao reproduzidos pelo codigo; eles nao foram editados manualmente.

## Catalogo canonico

O catalogo possui **133 termos**, dentro da faixa de 80 a 150 exigida. Ele foi composto por termos de tecnologia, dados, qualidade, infraestrutura, seguranca e negocio que ocorrem corretamente no corpus. Formas com erro nao entram no catalogo. A frequencia de palavras do corpus esta em `frequencia_palavras.csv` e serve de evidencia para essa selecao.

## Como funciona a DP

Para duas palavras `a` e `b`, `dp[i][j]` representa o menor custo para transformar os primeiros `i` caracteres de `a` nos primeiros `j` caracteres de `b`. Os casos-base sao `dp[i][0] = i` e `dp[0][j] = j`. Se os caracteres atuais forem iguais, a celula copia a diagonal; caso contrario, recebe `1 + min(remover, inserir, substituir)`. A matriz e preenchida de cima para baixo e da esquerda para a direita.

Uma comparacao custa **O(m*n)** em tempo e **O(m*n)** em memoria, onde `m` e `n` sao os tamanhos das palavras. Quando o catalogo cresce, cada palavra pendente precisa ser comparada com mais termos, aumentando o tempo aproximadamente de forma linear em relacao ao tamanho do catalogo. Uma otimizacao possivel seria guardar apenas duas linhas da matriz, reduzindo a memoria para O(n); o trade-off e perder a matriz completa para inspecao e depuracao.

## Regra de aceitacao

1. O termo e normalizado e comparado diretamente com o catalogo.
2. Se houver igualdade, recebe status `EXATO`, sem executar DP.
3. Se nao houver igualdade, a DP procura a menor distancia no catalogo.
4. Um unico candidato com distancia menor ou igual ao limite recebe `CORRIGIDO`.
5. Empate na menor distancia recebe `AMBIGUO` e o original e preservado.
6. Distancia acima do limite recebe `MANTIDO` e o original e preservado.

Palavras com menos de quatro caracteres nao passam pela aproximacao para reduzir falsos positivos.

## Limite 1 versus Limite 2

| Metrica | Limite 1 | Limite 2 |
|---|---:|---:|
| Termos analisados | 4199 | 4199 |
| EXATO | 1320 | 1320 |
| CORRIGIDO | 318 | 389 |
| AMBIGUO | 0 | 2 |
| MANTIDO | 2561 | 2488 |
| Registros alterados | 248 | 283 |

O limite 2 faz 71 correcoes a mais, mas tambem aumenta o risco. Ele corrige ausencias de acento como `solucao -> solução`, porem aproxima palavras semanticamente diferentes. O limite 1 e mais seguro para esta base porque corrige erros simples de digitacao, por exemplo `serkviço -> serviço`, `algxritmo -> algoritmo` e `sistqema -> sistema`, sem abrir margem para os falsos positivos mais frequentes do limite 2.

## Casos em que a distancia nao basta

- `producao` pode ficar empatada entre termos proximos como `producao` e `produto` dependendo da forma canonica e das operacoes exigidas. A DP mede apenas a forma, nao o contexto da frase; por isso o pipeline marca empate como ambiguo e mantem o original.
- Ausencias de acento ou cedilha podem custar duas operacoes, como em `funcao -> função`. Para uma pessoa, o erro e pequeno, mas a DP trata os caracteres individualmente.
- No limite 2, palavras como `revisar` e `revisou` podem ser aproximadas indevidamente de `revisão`. Isso mostra que proximidade grafica nao garante equivalencia de significado.

## Arquivos gerados

- `frequencia_palavras.csv`: frequencia observada no corpus.
- `transcricoes_processadas_L1.csv` e `transcricoes_processadas_L2.csv`: 420 registros com texto original, texto tratado e contadores por status.
- `correcoes_realizadas_L1.csv` e `correcoes_realizadas_L2.csv`: rastreabilidade de cada correcao automatica.
- `estatisticas_resumo_L1.csv`, `estatisticas_resumo_L2.csv` e `estatisticas_resumo.csv`: metricas dos dois limites e comparacao.

Os testes minimos solicitados sao executados automaticamente antes do corpus completo: limpeza, igualdade exata, distancia 1, dimensao da matriz e caso de empate.
