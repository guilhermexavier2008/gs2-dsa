"""
GS 2026.2 - Citizen Assist AI | Data Structures and Algorithms (DSA)

Sistema de gerenciamento e consulta de servicos e orientacoes ao cidadao.

Estrutura principal: lista encadeada simples implementada pela equipe
(classes No e ListaEncadeada), sem usar list/dict do Python para armazenar
os registros.

Algoritmos implementados no codigo:
  - Busca linear por identificador (percorre os nos ate encontrar).
  - Busca linear por atributo, com comparacao de trecho de texto manual.
  - Ordenacao Merge Sort adaptado para lista encadeada (religa os nos).

Execucao:  python citizen_assist.py
"""

import unicodedata

# ---------------------------------------------------------------------------
# Constantes e funcoes auxiliares de texto
# ---------------------------------------------------------------------------

CATEGORIAS = [
    "Documentos",
    "Assistência Social",
    "Educação",
    "Saúde",
    "Atendimento Comunitário",
    "Outros",
]

# Rotulo amigavel de cada campo (usado em mensagens e telas).
ROTULOS = {
    "id": "Identificador",
    "titulo": "Título",
    "categoria": "Categoria",
    "descricao": "Descrição",
    "publico_alvo": "Público-alvo",
    "canal": "Canal/Local de atendimento",
    "horario": "Horário de atendimento",
}


def normalizar(texto):
    """Minusculas e sem acentos, para comparar textos de forma justa."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def contem(texto, trecho):
    """Verifica se 'trecho' aparece em 'texto' (busca ingenua, feita a mao).

    Custo: O(n * m), com n = len(texto) e m = len(trecho).
    """
    n, m = len(texto), len(trecho)
    if m == 0 or m > n:
        return False
    for i in range(n - m + 1):
        j = 0
        while j < m and texto[i + j] == trecho[j]:
            j += 1
        if j == m:
            return True
    return False


def cortar(texto, tamanho):
    """Corta o texto para caber em uma coluna da tabela."""
    if len(texto) <= tamanho:
        return texto
    return texto[: tamanho - 3] + "..."


# ---------------------------------------------------------------------------
# Validacao de campos
# ---------------------------------------------------------------------------

def validar_campo(campo, valor):
    """Valida e devolve o valor limpo; levanta ValueError com mensagem clara."""
    rotulo = ROTULOS[campo]

    if campo == "id":
        texto = str(valor).strip()
        if texto == "":
            raise ValueError(f"{rotulo} não pode ficar vazio.")
        if not texto.isdigit():
            raise ValueError(f"{rotulo} deve conter apenas números inteiros positivos.")
        numero = int(texto)
        if numero <= 0:
            raise ValueError(f"{rotulo} deve ser maior que zero.")
        return numero

    texto = str(valor).strip()

    if campo == "horario":  # campo opcional
        return texto if texto else "Não informado"

    if texto == "":
        raise ValueError(f"{rotulo} é obrigatório e não pode ficar vazio.")

    if campo == "categoria":
        alvo = normalizar(texto)
        for categoria in CATEGORIAS:
            if normalizar(categoria) == alvo:
                return categoria
        raise ValueError(
            f"{rotulo} inválida. Use uma de: " + ", ".join(CATEGORIAS) + "."
        )

    minimos = {"titulo": 3, "descricao": 10, "publico_alvo": 3, "canal": 3}
    maximos = {"titulo": 80, "descricao": 300, "publico_alvo": 80, "canal": 120}
    if len(texto) < minimos.get(campo, 1):
        raise ValueError(f"{rotulo} muito curto (mínimo {minimos[campo]} caracteres).")
    if len(texto) > maximos.get(campo, 300):
        raise ValueError(f"{rotulo} muito longo (máximo {maximos[campo]} caracteres).")
    return texto


# ---------------------------------------------------------------------------
# Modelo de dados
# ---------------------------------------------------------------------------

class Servico:
    """Registro de um servico ou orientacao ao cidadao."""

    def __init__(self, id, titulo, categoria, descricao, publico_alvo, canal, horario=""):
        self.id = validar_campo("id", id)
        self.titulo = validar_campo("titulo", titulo)
        self.categoria = validar_campo("categoria", categoria)
        self.descricao = validar_campo("descricao", descricao)
        self.publico_alvo = validar_campo("publico_alvo", publico_alvo)
        self.canal = validar_campo("canal", canal)
        self.horario = validar_campo("horario", horario)

    def detalhes(self):
        linhas = ["-" * 60]
        for campo in ROTULOS:
            linhas.append(f"{ROTULOS[campo]}: {getattr(self, campo)}")
        linhas.append("-" * 60)
        return "\n".join(linhas)


class No:
    """No da lista encadeada: guarda um Servico e a referencia ao proximo no."""

    def __init__(self, servico):
        self.servico = servico
        self.proximo = None


# ---------------------------------------------------------------------------
# Lista encadeada
# ---------------------------------------------------------------------------

class ListaEncadeada:
    """Lista encadeada simples com referencias para inicio e fim.

    Invariantes:
      - inicio e None se e somente se a lista esta vazia (tamanho == 0);
      - fim aponta sempre para o ultimo no (fim.proximo e None);
      - tamanho e igual ao numero de nos alcancaveis a partir de inicio.
    """

    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def esta_vazia(self):
        return self.inicio is None

    # -- percurso ----------------------------------------------------------
    def __iter__(self):
        """Percorre a lista do inicio ao fim, devolvendo cada Servico. O(n)."""
        atual = self.inicio
        while atual is not None:
            yield atual.servico
            atual = atual.proximo

    # -- insercao ----------------------------------------------------------
    def _anexar(self, servico):
        """Insere no fim sem verificar duplicidade. O(1) gracas ao ponteiro 'fim'."""
        novo = No(servico)
        if self.inicio is None:
            self.inicio = novo
            self.fim = novo
        else:
            self.fim.proximo = novo
            self.fim = novo
        self.tamanho += 1

    def inserir(self, servico):
        """Insere no fim da lista garantindo identificador unico. O(n).

        O custo O(n) vem da checagem de duplicidade (percorre a lista);
        a insercao em si e O(1).
        """
        if self.buscar_por_id(servico.id) is not None:
            raise ValueError(f"Já existe um registro com o identificador {servico.id}.")
        self._anexar(servico)

    # -- busca -------------------------------------------------------------
    def buscar_por_id(self, id):
        """Busca linear pelo identificador. Melhor caso O(1), pior caso O(n)."""
        atual = self.inicio
        while atual is not None:
            if atual.servico.id == id:
                return atual.servico
            atual = atual.proximo
        return None

    def buscar_por_atributo(self, campo, termo):
        """Busca linear por trecho de texto em um atributo. O(n * m).

        Devolve uma NOVA ListaEncadeada com os registros encontrados
        (os objetos Servico sao compartilhados, apenas os nos sao novos).
        """
        resultado = ListaEncadeada()
        alvo = normalizar(termo)
        atual = self.inicio
        while atual is not None:
            valor = normalizar(str(getattr(atual.servico, campo)))
            if contem(valor, alvo):
                resultado._anexar(atual.servico)
            atual = atual.proximo
        return resultado

    # -- atualizacao -------------------------------------------------------
    def atualizar(self, id, novos_valores):
        """Atualiza campos de um registro existente (o id nao muda). O(n).

        Todos os valores sao validados antes de qualquer alteracao, de modo
        que uma entrada invalida nunca deixa o registro pela metade.
        Devolve True se atualizou, False se o id nao existe.
        """
        servico = self.buscar_por_id(id)
        if servico is None:
            return False
        validados = {}
        for campo, valor in novos_valores.items():
            if campo == "id":
                raise ValueError("O identificador não pode ser alterado.")
            validados[campo] = validar_campo(campo, valor)
        for campo, valor in validados.items():
            setattr(servico, campo, valor)
        return True

    # -- remocao -----------------------------------------------------------
    def remover(self, id):
        """Remove o no com o id informado, religando os vizinhos. O(n).

        Trata os tres casos: primeiro no, no do meio e ultimo no
        (atualizando 'fim'). Devolve o Servico removido ou None.
        """
        anterior = None
        atual = self.inicio
        while atual is not None and atual.servico.id != id:
            anterior = atual
            atual = atual.proximo
        if atual is None:
            return None
        if anterior is None:               # remove o primeiro
            self.inicio = atual.proximo
        else:                              # remove meio ou ultimo
            anterior.proximo = atual.proximo
        if atual is self.fim:              # removeu o ultimo
            self.fim = anterior
        atual.proximo = None
        self.tamanho -= 1
        return atual.servico

    # -- ordenacao (Merge Sort para lista encadeada) -------------------------
    @staticmethod
    def _chave(servico, criterio):
        if criterio == "id":
            return servico.id
        return normalizar(str(getattr(servico, criterio)))

    @staticmethod
    def _dividir(cabeca):
        """Divide a lista ao meio (ponteiros lento/rapido) e devolve a 2a metade."""
        lento = cabeca
        rapido = cabeca.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        segunda = lento.proximo
        lento.proximo = None
        return segunda

    def _mesclar(self, a, b, criterio, decrescente):
        """Intercala duas listas ja ordenadas, religando os nos. Estavel."""
        sentinela = No(None)
        cauda = sentinela
        while a is not None and b is not None:
            ka = self._chave(a.servico, criterio)
            kb = self._chave(b.servico, criterio)
            pegar_a = (ka >= kb) if decrescente else (ka <= kb)
            if pegar_a:
                cauda.proximo = a
                a = a.proximo
            else:
                cauda.proximo = b
                b = b.proximo
            cauda = cauda.proximo
        cauda.proximo = a if a is not None else b
        return sentinela.proximo

    def _merge_sort(self, cabeca, criterio, decrescente):
        if cabeca is None or cabeca.proximo is None:
            return cabeca
        segunda = self._dividir(cabeca)
        esquerda = self._merge_sort(cabeca, criterio, decrescente)
        direita = self._merge_sort(segunda, criterio, decrescente)
        return self._mesclar(esquerda, direita, criterio, decrescente)

    def ordenar(self, criterio, decrescente=False):
        """Ordena a propria lista por 'criterio'. O(n log n) tempo."""
        if criterio not in ROTULOS:
            raise ValueError(f"Critério de ordenação inválido: {criterio}")
        self.inicio = self._merge_sort(self.inicio, criterio, decrescente)
        # recalcula o ponteiro 'fim' (percurso O(n), nao altera a ordem de grandeza)
        atual = self.inicio
        self.fim = None
        while atual is not None:
            self.fim = atual
            atual = atual.proximo


# ---------------------------------------------------------------------------
# Dados de exemplo (fictícios)
# ---------------------------------------------------------------------------

DADOS_EXEMPLO = [
    (105, "Emissão de RG", "Documentos",
     "Emissão da primeira e da segunda via da carteira de identidade.",
     "Maiores de 18 anos e menores acompanhados", "Posto de identificação - Centro", "Seg a Sex, 8h às 16h"),
    (101, "Cadastro Único (CadÚnico)", "Assistência Social",
     "Inscrição de famílias de baixa renda em programas sociais.",
     "Famílias com renda per capita de até meio salário mínimo", "CRAS do bairro", "Seg a Sex, 8h às 17h"),
    (110, "Matrícula na rede municipal", "Educação",
     "Matrícula de crianças e adolescentes no ensino fundamental.",
     "Responsáveis por estudantes de 6 a 14 anos", "Portal da Educação (online)", "24 horas"),
    (103, "Vacinação infantil", "Saúde",
     "Aplicação das vacinas do calendário nacional de imunização.",
     "Crianças de 0 a 12 anos", "UBS mais próxima", "Seg a Sex, 7h às 17h"),
    (108, "Mutirão de limpeza do bairro", "Atendimento Comunitário",
     "Ação voluntária de limpeza de praças e córregos.",
     "Moradores do bairro", "Associação de moradores", "Sábados, 9h"),
    (102, "Emissão de CPF", "Documentos",
     "Inscrição e regularização do Cadastro de Pessoas Físicas.",
     "Qualquer cidadão", "Agências dos Correios e site da Receita", "Horário da agência"),
    (107, "Bolsa Família - consulta de benefício", "Assistência Social",
     "Consulta de situação e calendário de pagamento do benefício.",
     "Beneficiários do programa", "Aplicativo oficial e CRAS", "24 horas"),
    (104, "Consulta médica básica", "Saúde",
     "Atendimento clínico geral e encaminhamento para especialistas.",
     "Moradores da área de cobertura", "UBS do bairro", "Seg a Sex, 7h às 16h"),
]


def carregar_exemplos(lista):
    """Insere os dados de exemplo; ignora ids ja existentes. Devolve a qtd. inserida."""
    inseridos = 0
    for dados in DADOS_EXEMPLO:
        servico = Servico(*dados)
        if lista.buscar_por_id(servico.id) is None:
            lista._anexar(servico)
            inseridos += 1
    return inseridos


# ---------------------------------------------------------------------------
# Interface de terminal (menu interativo)
# ---------------------------------------------------------------------------

def imprimir_tabela(lista):
    print(f"{'ID':<6}{'Título':<34}{'Categoria':<25}{'Canal':<30}")
    print("-" * 95)
    for s in lista:
        print(f"{s.id:<6}{cortar(s.titulo, 32):<34}{cortar(s.categoria, 23):<25}{cortar(s.canal, 28):<30}")
    print("-" * 95)
    print(f"Total: {lista.tamanho} registro(s).")


def pedir_campo(campo, atual=None):
    """Le um campo repetindo ate ser valido. Se 'atual' existir, Enter mantem o valor."""
    rotulo = ROTULOS[campo]
    while True:
        if atual is not None:
            valor = input(f"{rotulo} [{cortar(str(atual), 40)}] (Enter mantém): ")
            if valor.strip() == "":
                return atual
        else:
            valor = input(f"{rotulo}: ")
        try:
            return validar_campo(campo, valor)
        except ValueError as erro:
            print(f"  ✗ {erro}")


def pedir_categoria(atual=None):
    """Mostra as categorias e aceita o numero ou o nome."""
    print("Categorias:")
    for i, nome in enumerate(CATEGORIAS, start=1):
        print(f"  {i}) {nome}")
    while True:
        if atual is not None:
            valor = input(f"Categoria [{atual}] (número ou nome, Enter mantém): ").strip()
            if valor == "":
                return atual
        else:
            valor = input("Categoria (número ou nome): ").strip()
        if valor.isdigit() and 1 <= int(valor) <= len(CATEGORIAS):
            return CATEGORIAS[int(valor) - 1]
        try:
            return validar_campo("categoria", valor)
        except ValueError as erro:
            print(f"  ✗ {erro}")


def pedir_id(mensagem="Identificador: "):
    while True:
        valor = input(mensagem)
        try:
            return validar_campo("id", valor)
        except ValueError as erro:
            print(f"  ✗ {erro}")


def pedir_escolha(opcoes, titulo):
    """Mostra opcoes numeradas (lista de tuplas (chave, texto)) e devolve a chave."""
    print(titulo)
    for i, (_, texto) in enumerate(opcoes, start=1):
        print(f"  {i}) {texto}")
    while True:
        valor = input("Escolha: ").strip()
        if valor.isdigit() and 1 <= int(valor) <= len(opcoes):
            return opcoes[int(valor) - 1][0]
        print(f"  ✗ Opção inválida. Digite um número de 1 a {len(opcoes)}.")


def opcao_cadastrar(lista):
    print("\n=== Cadastrar novo serviço/orientação ===")
    while True:
        id_ = pedir_id()
        if lista.buscar_por_id(id_) is not None:
            print(f"  ✗ Identificador {id_} já está em uso. Escolha outro.")
            continue
        break
    titulo = pedir_campo("titulo")
    categoria = pedir_categoria()
    descricao = pedir_campo("descricao")
    publico = pedir_campo("publico_alvo")
    canal = pedir_campo("canal")
    horario = pedir_campo("horario")
    lista.inserir(Servico(id_, titulo, categoria, descricao, publico, canal, horario))
    print(f"✓ Serviço {id_} cadastrado com sucesso.")


def opcao_consultar(lista):
    print("\n=== Consultar por identificador ===")
    if lista.esta_vazia():
        print("A lista está vazia. Cadastre registros primeiro.")
        return
    id_ = pedir_id()
    servico = lista.buscar_por_id(id_)
    if servico is None:
        print(f"Registro com identificador {id_} não encontrado.")
    else:
        print(servico.detalhes())


def opcao_listar(lista):
    print("\n=== Todos os registros ===")
    if lista.esta_vazia():
        print("A lista está vazia. Nenhum registro cadastrado.")
        return
    imprimir_tabela(lista)


def opcao_atualizar(lista):
    print("\n=== Atualizar registro ===")
    if lista.esta_vazia():
        print("A lista está vazia. Nada para atualizar.")
        return
    id_ = pedir_id()
    servico = lista.buscar_por_id(id_)
    if servico is None:
        print(f"Registro com identificador {id_} não encontrado.")
        return
    print(servico.detalhes())
    print("Pressione Enter para manter o valor atual de cada campo.")
    novos = {
        "titulo": pedir_campo("titulo", servico.titulo),
        "categoria": pedir_categoria(servico.categoria),
        "descricao": pedir_campo("descricao", servico.descricao),
        "publico_alvo": pedir_campo("publico_alvo", servico.publico_alvo),
        "canal": pedir_campo("canal", servico.canal),
        "horario": pedir_campo("horario", servico.horario),
    }
    lista.atualizar(id_, novos)
    print(f"✓ Registro {id_} atualizado.")


def opcao_excluir(lista):
    print("\n=== Excluir registro ===")
    if lista.esta_vazia():
        print("A lista está vazia. Nada para excluir.")
        return
    id_ = pedir_id()
    servico = lista.buscar_por_id(id_)
    if servico is None:
        print(f"Registro com identificador {id_} não encontrado.")
        return
    print(servico.detalhes())
    while True:
        resp = input("Confirma a exclusão? (s/n): ").strip().lower()
        if resp in ("s", "n"):
            break
        print("  ✗ Responda apenas com 's' ou 'n'.")
    if resp == "s":
        lista.remover(id_)
        print(f"✓ Registro {id_} excluído.")
    else:
        print("Exclusão cancelada.")


def opcao_pesquisar(lista):
    print("\n=== Pesquisar registros ===")
    if lista.esta_vazia():
        print("A lista está vazia. Nada para pesquisar.")
        return
    campo = pedir_escolha(
        [("titulo", "Título"), ("categoria", "Categoria"),
         ("publico_alvo", "Público-alvo"), ("canal", "Canal/Local"),
         ("descricao", "Descrição")],
        "Pesquisar por qual atributo?",
    )
    while True:
        termo = input("Termo de busca: ").strip()
        if termo:
            break
        print("  ✗ O termo de busca não pode ficar vazio.")
    achados = lista.buscar_por_atributo(campo, termo)
    if achados.esta_vazia():
        print(f"Nenhum registro encontrado para '{termo}' em {ROTULOS[campo]}.")
    else:
        print(f"Resultado da busca por '{termo}':")
        imprimir_tabela(achados)


def opcao_ordenar(lista):
    print("\n=== Ordenar registros ===")
    if lista.esta_vazia():
        print("A lista está vazia. Nada para ordenar.")
        return
    criterio = pedir_escolha(
        [("id", "Identificador"), ("titulo", "Título"), ("categoria", "Categoria")],
        "Ordenar por qual critério?",
    )
    sentido = pedir_escolha(
        [(False, "Crescente (A-Z / menor para maior)"),
         (True, "Decrescente (Z-A / maior para menor)")],
        "Em qual sentido?",
    )
    lista.ordenar(criterio, decrescente=sentido)
    print(f"✓ Lista ordenada por {ROTULOS[criterio]} "
          f"({'decrescente' if sentido else 'crescente'}).")
    imprimir_tabela(lista)


def opcao_exemplos(lista):
    qtd = carregar_exemplos(lista)
    if qtd == 0:
        print("Os dados de exemplo já estavam carregados (nenhum registro novo).")
    else:
        print(f"✓ {qtd} registro(s) de exemplo (fictícios) carregado(s).")


MENU = """
================ CITIZEN ASSIST AI ================
 1) Cadastrar serviço/orientação
 2) Consultar por identificador
 3) Listar todos
 4) Atualizar registro
 5) Excluir registro
 6) Pesquisar (por atributo)
 7) Ordenar
 8) Carregar dados de exemplo
 0) Sair
==================================================="""

ACOES = {
    "1": opcao_cadastrar,
    "2": opcao_consultar,
    "3": opcao_listar,
    "4": opcao_atualizar,
    "5": opcao_excluir,
    "6": opcao_pesquisar,
    "7": opcao_ordenar,
    "8": opcao_exemplos,
}


def main(lista=None):
    if lista is None:
        lista = ListaEncadeada()
    try:
        while True:
            print(MENU)
            escolha = input("Escolha uma opção: ").strip()
            if escolha == "0":
                print("Encerrando o Citizen Assist AI. Até logo!")
                break
            acao = ACOES.get(escolha)
            if acao is None:
                print("✗ Opção inexistente. Digite um número de 0 a 8.")
                continue
            acao(lista)
    except EOFError:
        print("\nEntrada encerrada. Saindo do sistema.")
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. Saindo do sistema.")


if __name__ == "__main__":
    main()
