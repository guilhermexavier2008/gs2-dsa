"""
Testes e evidencias - GS 2026.2 Citizen Assist AI (DSA)

Executa cenarios automaticos que simulam o uso do menu (entradas digitadas),
comparam o resultado esperado com o observado e salvam:
  - evidencias_testes.txt  (transcricao completa de cada cenario, como no terminal)
  - resultados_testes.json (resumo usado na documentacao)

Execucao:  python testes.py
"""

import builtins
import contextlib
import io
import json

import citizen_assist as ca


def executar_menu(entradas, lista=None):
    """Roda main() com as 'entradas' simuladas e devolve (transcricao, lista)."""
    if lista is None:
        lista = ca.ListaEncadeada()
    fila = list(entradas)
    saida = io.StringIO()

    def input_falso(prompt=""):
        if not fila:
            raise EOFError
        valor = fila.pop(0)
        print(f"{prompt}{valor}")          # ecoa como se fosse o terminal
        return valor

    original = builtins.input
    builtins.input = input_falso
    try:
        with contextlib.redirect_stdout(saida):
            ca.main(lista)
    finally:
        builtins.input = original
    return saida.getvalue(), lista


def com_exemplos():
    lista = ca.ListaEncadeada()
    ca.carregar_exemplos(lista)
    return lista


def ids(lista):
    return [s.id for s in lista]


def invariantes_ok(lista):
    """Confere tamanho, inicio/fim e ligacao dos nos."""
    n, atual, ultimo = 0, lista.inicio, None
    while atual is not None:
        n += 1
        ultimo = atual
        atual = atual.proximo
    return n == lista.tamanho and ultimo is lista.fim and (lista.inicio is None) == (lista.tamanho == 0)


CAD_201 = ["1", "201", "Segunda via de certidão", "1", "Emissão de segunda via de certidão de nascimento ou casamento.",
           "Qualquer cidadão", "Cartório de registro civil", "Seg a Sex, 9h às 16h"]

CENARIOS = []


def cenario(id, nome, pre, entrada, esperado, func):
    CENARIOS.append(dict(id=id, nome=nome, pre=pre, entrada=entrada, esperado=esperado, func=func))


def tem(texto, *trechos):
    return all(t in texto for t in trechos)


# ---- T01 lista vazia ------------------------------------------------------
def t01():
    ent = ["3", "2", "4", "5", "6", "7", "0"]
    t, l = executar_menu(ent)
    ok = t.count("A lista está vazia") == 6 and l.tamanho == 0
    return t, ok, f"Mensagem 'A lista está vazia' exibida {t.count('A lista está vazia')} vez(es); tamanho = {l.tamanho}"

cenario("T01", "Operações sobre lista vazia (listar, consultar, atualizar, excluir, pesquisar, ordenar)",
        "Lista vazia", "3, 2, 4, 5, 6, 7, 0",
        "Cada operação informa 'A lista está vazia' sem erro; sistema não quebra", t01)


# ---- T02 cadastro valido --------------------------------------------------
def t02():
    t, l = executar_menu(CAD_201 + ["3", "0"])
    s = l.buscar_por_id(201)
    ok = tem(t, "Serviço 201 cadastrado com sucesso") and s is not None and s.categoria == "Documentos" and l.tamanho == 1
    return t, ok, f"Registro 201 encontrado: {s.titulo if s else None}; categoria = {s.categoria if s else None}; tamanho = {l.tamanho}"

cenario("T02", "Cadastro válido de um serviço", "Lista vazia",
        "1 → id 201, título, categoria 1, descrição, público, canal, horário; depois 3 (listar)",
        "Mensagem de sucesso; registro aparece na listagem (total 1)", t02)


# ---- T03 campos invalidos no cadastro --------------------------------------
def t03():
    ent = ["1",
           "", "abc", "0", "-5", "7.5", "301",                     # id invalido x6, depois valido
           "", "ab", "Orientação sobre IPTU",                     # titulo vazio, curto, valido
           "99", "esporte", "Outros",                              # categoria invalida x2, valida
           "", "curta", "Orientações sobre pagamento e isenção do IPTU.",   # descricao
           "", "Proprietários de imóveis",                         # publico vazio, valido
           "  ", "Secretaria da Fazenda",                          # canal so espacos, valido
           "",                                                     # horario opcional vazio
           "3", "0"]
    t, l = executar_menu(ent)
    s = l.buscar_por_id(301)
    ok = (tem(t, "Identificador não pode ficar vazio", "apenas números inteiros positivos", "maior que zero",
              "Título é obrigatório", "muito curto", "Categoria inválida", "Descrição muito curto",
              "Público-alvo é obrigatório", "Canal/Local de atendimento é obrigatório")
          and s is not None and s.horario == "Não informado" and l.tamanho == 1)
    return t, ok, ("Cada entrada inválida gerou mensagem e foi pedida novamente; registro 301 salvo com "
                   f"horário '{s.horario if s else None}'; tamanho = {l.tamanho}")

cenario("T03", "Cadastro com entradas inválidas (vazios, texto no id, zero, negativo, categoria inexistente, textos curtos)",
        "Lista vazia",
        "id: '', 'abc', '0', '-5', '7.5' e depois 301; título: '', 'ab'; categoria: '99', 'esporte'; descrição/público/canal vazios ou curtos",
        "Mensagem clara para cada erro, o campo é solicitado novamente e só então o registro é salvo", t03)


# ---- T04 id duplicado -------------------------------------------------------
def t04():
    ent = CAD_201 + ["1", "201", "202", "Matrícula em creche", "3",
                     "Cadastro de crianças de 0 a 3 anos em creches municipais.",
                     "Responsáveis por crianças pequenas", "Portal da Educação", "", "0"]
    t, l = executar_menu(ent)
    ok = tem(t, "Identificador 201 já está em uso") and ids(l) == [201, 202] and l.tamanho == 2
    return t, ok, f"Mensagem de duplicidade exibida; ids na lista = {ids(l)}"

cenario("T04", "Identificador duplicado", "Registro 201 já cadastrado",
        "1 → id 201 (duplicado); depois id 202 e demais campos",
        "Mensagem 'já está em uso'; novo id aceito; lista com 2 registros (201 e 202)", t04)


# ---- T05 exemplos e listagem -------------------------------------------------
def t05():
    t, l = executar_menu(["8", "3", "8", "0"])
    ok = tem(t, "8 registro(s) de exemplo", "Total: 8 registro(s)", "nenhum registro novo") and l.tamanho == 8
    return t, ok, f"Carga de 8 registros, listagem com 'Total: 8' e segunda carga sem duplicar; tamanho = {l.tamanho}"

cenario("T05", "Carregar dados de exemplo e listar todos (e repetir a carga)", "Lista vazia",
        "8, 3, 8, 0", "8 registros carregados e listados; segunda carga não duplica", t05)


# ---- T06 consulta existente ----------------------------------------------
def t06():
    t, l = executar_menu(["2", "103", "0"], com_exemplos())
    ok = tem(t, "Título: Vacinação infantil", "Categoria: Saúde", "Identificador: 103")
    return t, ok, "Detalhes completos do registro 103 exibidos (Vacinação infantil / Saúde)"

cenario("T06", "Consultar registro pelo identificador (existente)", "8 registros de exemplo",
        "2 → 103", "Exibe todos os campos do registro 103", t06)


# ---- T07 consulta inexistente / invalida -----------------------------------
def t07():
    t, l = executar_menu(["2", "xyz", "999", "0"], com_exemplos())
    ok = tem(t, "apenas números inteiros positivos", "Registro com identificador 999 não encontrado")
    return t, ok, "Entrada 'xyz' rejeitada; id 999 retornou 'não encontrado'"

cenario("T07", "Consultar identificador inexistente e valor incompatível", "8 registros de exemplo",
        "2 → 'xyz', depois 999", "Erro de formato para 'xyz'; mensagem 'não encontrado' para 999", t07)


# ---- T08 atualizar ----------------------------------------------------------
def t08():
    ent = ["4", "103", "Vacinação infantil e de adultos", "", "", "", "", "Seg a Sáb, 7h às 17h", "2", "103", "0"]
    # observe: Enter mantem categoria (campo 'Categoria' le 1 linha vazia)
    t, l = executar_menu(ent, com_exemplos())
    s = l.buscar_por_id(103)
    ok = (tem(t, "Registro 103 atualizado") and s.titulo == "Vacinação infantil e de adultos"
          and s.categoria == "Saúde" and s.horario == "Seg a Sáb, 7h às 17h" and s.id == 103)
    return t, ok, f"Título = '{s.titulo}'; categoria mantida = '{s.categoria}'; horário = '{s.horario}'"

cenario("T08", "Atualizar registro existente (alterar título e horário, manter o resto com Enter)", "8 registros de exemplo",
        "4 → 103; novo título; Enter nos campos a manter; novo horário; depois 2 → 103",
        "Registro atualizado; campos não alterados permanecem; consulta mostra novos valores", t08)


# ---- T09 atualizar invalido ---------------------------------------------------
def t09():
    ent = ["4", "103", "ab", "Vacinação em campanha", "", "", "", "", "", "0"]
    t, l = executar_menu(ent, com_exemplos())
    s = l.buscar_por_id(103)
    ok = tem(t, "Título muito curto", "Registro 103 atualizado") and s.titulo == "Vacinação em campanha"
    return t, ok, f"Título 'ab' rejeitado; valor válido gravado: '{s.titulo}'"

cenario("T09", "Atualizar com valor inválido", "8 registros de exemplo",
        "4 → 103; título 'ab' (inválido) e depois 'Vacinação em campanha'",
        "Mensagem de erro, campo pedido novamente e atualização concluída com valor válido", t09)


# ---- T10 atualizar inexistente ------------------------------------------------
def t10():
    t, l = executar_menu(["4", "999", "0"], com_exemplos())
    ok = tem(t, "Registro com identificador 999 não encontrado") and l.tamanho == 8
    return t, ok, "Mensagem 'não encontrado'; lista inalterada (8 registros)"

cenario("T10", "Atualizar identificador inexistente", "8 registros de exemplo",
        "4 → 999", "Mensagem 'não encontrado'; nada é alterado", t10)


# ---- T11 excluir com confirmacao -----------------------------------------------
def t11():
    ent = ["5", "104", "x", "s", "5", "108", "n", "5", "999", "0"]
    t, l = executar_menu(ent, com_exemplos())
    ok = (tem(t, "Responda apenas com 's' ou 'n'", "Registro 104 excluído", "Exclusão cancelada",
              "Registro com identificador 999 não encontrado")
          and l.buscar_por_id(104) is None and l.buscar_por_id(108) is not None and l.tamanho == 7
          and invariantes_ok(l))
    return t, ok, f"104 excluído; 108 mantido (cancelado); 999 não encontrado; tamanho = {l.tamanho}; invariantes OK"

cenario("T11", "Excluir registro (confirmação inválida, confirmação 's', cancelamento 'n' e id inexistente)",
        "8 registros de exemplo", "5 → 104, 'x', 's'; 5 → 108, 'n'; 5 → 999",
        "104 removido; 108 permanece; 999 'não encontrado'; total passa de 8 para 7", t11)


# ---- T12 remocao em posicoes (estrutura) ---------------------------------------
def t12():
    l = ca.ListaEncadeada()
    for i in (1, 2, 3, 4, 5):
        l.inserir(ca.Servico(i, f"Serviço {i}", "Outros", "Descrição do serviço de teste.", "Todos", "Balcão"))
    r1 = l.remover(1)                       # primeiro
    r3 = l.remover(3)                       # meio
    r5 = l.remover(5)                       # ultimo
    r9 = l.remover(9)                       # inexistente
    l.inserir(ca.Servico(6, "Serviço 6", "Outros", "Descrição do serviço de teste.", "Todos", "Balcão"))
    ok = (ids(l) == [2, 4, 6] and r1.id == 1 and r3.id == 3 and r5.id == 5 and r9 is None
          and l.fim.servico.id == 6 and l.inicio.servico.id == 2 and invariantes_ok(l))
    while not l.esta_vazia():
        l.remover(l.inicio.servico.id)
    ok = ok and l.inicio is None and l.fim is None and l.tamanho == 0
    obs = "Removidos primeiro, meio e último; ids restantes [2, 4, 6] após novo insert; lista esvaziada com inicio=fim=None"
    return "(teste de estrutura, sem menu)\n" + obs, ok, obs

cenario("T12", "Remoção no início, no meio e no fim da lista encadeada (ponteiros início/fim)",
        "Lista com ids 1 a 5", "remover(1), remover(3), remover(5), remover(9), inserir(6), esvaziar",
        "Ligações corretas; ids [2, 4, 6]; 'fim' atualizado; lista vazia termina com início e fim nulos", t12)


# ---- T13/T14/T15 pesquisa -----------------------------------------------------
def t13():
    t, l = executar_menu(["6", "1", "EMISSAO", "0"], com_exemplos())
    ok = tem(t, "Emissão de RG", "Emissão de CPF", "Total: 2 registro(s)") and "Vacinação" not in t.split("Resultado")[1]
    return t, ok, "Busca 'EMISSAO' (sem acento/maiúsculas) retornou RG (105) e CPF (102): Total 2"

cenario("T13", "Pesquisar por título (ignora maiúsculas e acentos)", "8 registros de exemplo",
        "6 → 1 (título) → 'EMISSAO'", "Retorna 'Emissão de RG' e 'Emissão de CPF' (2 registros)", t13)


def t14():
    t, l = executar_menu(["6", "2", "saude", "6", "3", "MORADORES", "0"], com_exemplos())
    ok = (t.count("Total: 2 registro(s)") == 2 and "Vacinação infantil" in t and "Consulta médica básica" in t
          and "Mutirão de limpeza do bairro" in t)
    return t, ok, "Categoria 'saude' → 2 registros (103, 104); público 'MORADORES' → 2 registros (108, 104)"

cenario("T14", "Pesquisar por categoria e por público-alvo", "8 registros de exemplo",
        "6 → 2 → 'saude'; 6 → 3 → 'MORADORES'", "2 registros em cada pesquisa", t14)


def t15():
    t, l = executar_menu(["6", "1", "", "zzz", "6", "9", "1", "xyz", "0"], com_exemplos())
    ok = tem(t, "O termo de busca não pode ficar vazio", "Nenhum registro encontrado para 'zzz'", "Opção inválida", "Nenhum registro encontrado para 'xyz'")
    return t, ok, "Termo vazio rejeitado; 'zzz' e 'xyz' sem resultados; opção '9' inválida no submenu"

cenario("T15", "Pesquisa com termo vazio, sem resultados e opção inválida no submenu", "8 registros de exemplo",
        "6 → 1 → '' → 'zzz'; 6 → 9 → 1 → 'xyz'", "Mensagens claras de erro e de 'nenhum registro encontrado'", t15)


# ---- T16/T17/T18 ordenacao ---------------------------------------------------------
def t16():
    t, l = executar_menu(["7", "1", "1", "0"], com_exemplos())
    ok = ids(l) == [101, 102, 103, 104, 105, 107, 108, 110] and invariantes_ok(l)
    return t, ok, f"Ordem dos ids após ordenar: {ids(l)}"

cenario("T16", "Ordenar por identificador (crescente)", "8 registros de exemplo (inseridos fora de ordem)",
        "7 → 1 (id) → 1 (crescente)", "ids em ordem 101, 102, 103, 104, 105, 107, 108, 110", t16)


def t17():
    t, l = executar_menu(["7", "2", "2", "0"], com_exemplos())
    titulos = [s.titulo for s in l]
    esperado = ["Vacinação infantil", "Mutirão de limpeza do bairro", "Matrícula na rede municipal",
                "Emissão de RG", "Emissão de CPF", "Consulta médica básica",
                "Cadastro Único (CadÚnico)", "Bolsa Família - consulta de benefício"]
    ok = titulos == esperado and invariantes_ok(l)
    return t, ok, f"Títulos em ordem decrescente: {titulos}"

cenario("T17", "Ordenar por título (decrescente)", "8 registros de exemplo",
        "7 → 2 (título) → 2 (decrescente)", "Títulos de Z para A (ignorando acentos)", t17)


def t18():
    t, l = executar_menu(["7", "3", "1", "0"], com_exemplos())
    cats = [s.categoria for s in l]
    esperado = ["Assistência Social", "Assistência Social", "Atendimento Comunitário", "Documentos",
                "Documentos", "Educação", "Saúde", "Saúde"]
    # estabilidade: dentro da mesma categoria, mantem a ordem original de insercao (105 antes de 102; 101 antes de 107; 103 antes de 104)
    ok = cats == esperado and ids(l) == [101, 107, 108, 105, 102, 110, 103, 104]
    return t, ok, f"Categorias: {cats}; ids: {ids(l)} (ordenação estável)"

cenario("T18", "Ordenar por categoria (crescente, estável)", "8 registros de exemplo",
        "7 → 3 (categoria) → 1 (crescente)", "Categorias em ordem alfabética; empates mantêm a ordem original", t18)


def t19():
    l = ca.ListaEncadeada()
    l.ordenar("titulo")                                  # lista vazia
    vazio_ok = l.esta_vazia() and invariantes_ok(l)
    l.inserir(ca.Servico(1, "Único serviço", "Outros", "Descrição do serviço único.", "Todos", "Balcão"))
    l.ordenar("id", decrescente=True)                    # um elemento
    um_ok = ids(l) == [1] and l.fim is l.inicio and invariantes_ok(l)
    try:
        l.ordenar("inexistente")
        erro_ok = False
    except ValueError:
        erro_ok = True
    ok = vazio_ok and um_ok and erro_ok
    obs = "Ordenar lista vazia e lista com 1 elemento funciona; critério inexistente levanta ValueError"
    return "(teste de estrutura, sem menu)\n" + obs, ok, obs

cenario("T19", "Ordenação em casos limite (lista vazia, 1 elemento, critério inválido)", "Listas pequenas",
        "ordenar() com 0 e 1 elemento; critério 'inexistente'", "Sem erros nos casos válidos; ValueError no critério inválido", t19)


# ---- T20 menu invalido ------------------------------------------------------------
def t20():
    t, l = executar_menu(["9", "abc", "", "-1", "1.5", "0"])
    ok = t.count("Opção inexistente") == 5 and "Encerrando o Citizen Assist AI" in t
    return t, ok, f"'Opção inexistente' exibida {t.count('Opção inexistente')} vezes; sistema encerrou normalmente com '0'"

cenario("T20", "Opções inválidas no menu principal e saída", "Lista vazia",
        "9, 'abc', '' , -1, 1.5, 0", "5 mensagens de opção inexistente; opção 0 encerra o programa", t20)


# ---- T21 EOF -----------------------------------------------------------------------
def t21():
    t, l = executar_menu(["3"])
    ok = "Entrada encerrada" in t
    return t, ok, "Fim da entrada (Ctrl+D/Ctrl+Z) tratado sem erro: 'Entrada encerrada. Saindo do sistema.'"

cenario("T21", "Encerramento inesperado da entrada (EOF)", "Lista vazia", "3 e fim da entrada",
        "Programa termina com mensagem amigável, sem traceback", t21)


# ---- T22 volume ---------------------------------------------------------------------
def t22():
    import random
    random.seed(7)
    l = ca.ListaEncadeada()
    numeros = list(range(1, 2001))
    random.shuffle(numeros)
    for n in numeros:
        l.inserir(ca.Servico(n, f"Serviço {random.randint(1, 500):04d}", "Outros",
                             "Registro gerado para teste de volume.", "Todos", "Balcão"))
    l.ordenar("id")
    ok1 = ids(l) == list(range(1, 2001)) and invariantes_ok(l)
    l.ordenar("titulo", decrescente=True)
    chaves = [ca.normalizar(s.titulo) for s in l]
    ok2 = all(chaves[i] >= chaves[i + 1] for i in range(len(chaves) - 1)) and l.tamanho == 2000 and invariantes_ok(l)
    try:
        l.inserir(ca.Servico(1000, "Duplicado", "Outros", "Registro duplicado de teste.", "Todos", "Balcão"))
        ok3 = False
    except ValueError:
        ok3 = True
    obs = "2000 registros inseridos fora de ordem; ordenação por id e por título (decrescente) correta; duplicado rejeitado"
    return "(teste de volume, sem menu)\n" + obs, ok1 and ok2 and ok3, obs

cenario("T22", "Teste de volume (2000 registros)", "Lista vazia",
        "2000 inserções aleatórias; ordenar por id; ordenar por título decrescente; inserir id repetido",
        "Ordem correta nas duas ordenações; invariantes mantidos; duplicado rejeitado", t22)


# ---------------------------------------------------------------------------
def main():
    resultados = []
    with open("evidencias_testes.txt", "w", encoding="utf-8") as arq:
        for c in CENARIOS:
            transcricao, ok, observado = c["func"]()
            status = "PASSOU" if ok else "FALHOU"
            print(f"[{status}] {c['id']} - {c['nome']}")
            arq.write("=" * 78 + "\n")
            arq.write(f"{c['id']} - {c['nome']}\n")
            arq.write(f"Pré-condição : {c['pre']}\n")
            arq.write(f"Entrada      : {c['entrada']}\n")
            arq.write(f"Esperado     : {c['esperado']}\n")
            arq.write(f"Observado    : {observado}\n")
            arq.write(f"Resultado    : {status}\n")
            arq.write("--- saída do terminal ---\n")
            arq.write(transcricao.replace(ca.MENU + "\n", "[menu principal]\n") + "\n")
            resultados.append(dict(id=c["id"], nome=c["nome"], pre=c["pre"], entrada=c["entrada"],
                                   esperado=c["esperado"], observado=observado, status=status))
    with open("resultados_testes.json", "w", encoding="utf-8") as arq:
        json.dump(resultados, arq, ensure_ascii=False, indent=2)
    total = len(resultados)
    passou = sum(1 for r in resultados if r["status"] == "PASSOU")
    print(f"\n{passou}/{total} cenários passaram.")


if __name__ == "__main__":
    main()
