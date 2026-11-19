# GS 2026.2 — Citizen Assist AI (DSA)

Sistema em Python para gerenciar e consultar serviços e orientações ao cidadão, usando **lista encadeada implementada pela equipe**, busca linear e ordenação **Merge Sort**.

## Equipe
- Guilherme Xavier — RM 573053
- Beckman Lugli — RM 573442
- Bryan Lugli — RM 571350

## Como executar
Requisito: Python 3.8+ (sem dependências externas).

```
python citizen_assist.py   # sistema com menu interativo
python testes.py           # 22 cenários automáticos (gera evidencias_testes.txt)
```

Dica: no menu, a opção 8 carrega 8 registros fictícios.

## Arquivos
| Arquivo | Conteúdo |
|---|---|
| `citizen_assist.py` | Código-fonte (No, ListaEncadeada, Servico, menu) |
| `testes.py` | Cenários de teste automáticos |
| `evidencias_testes.txt` | Saída de terminal de cada cenário |
| `resultados_testes.json` | Resumo dos testes |
| `Documentacao_Tecnica_Citizen_Assist_AI.docx` | Documentação técnica, Big-O e evidências |

## Resumo da análise Big-O (n = nº de registros)
Inserção O(n) (checa id duplicado; a ligação em si é O(1)) · Busca por id O(n) · Atualização O(n) · Exclusão O(n) · Ordenação O(n log n). Detalhes na documentação.
