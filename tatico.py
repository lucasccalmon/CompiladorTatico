import ply.lex as lex
import ply.yacc as yacc

# -----------------------------------------------------------------------------
# 1. ANÁLISE LÉXICA
# Definição dos tokens que nossa linguagem entende
# -----------------------------------------------------------------------------

tokens = (
    'TIME', 'FORMACAO', 'VALIDAR',
    'POSICAO',  # GOL, DEF, MEI, ATA
    'CODIGO_FORMACAO', # Ex: 4-4-2, 4-3-3
    'NUMERO', 'NOME',
    'DOIS_PONTOS', 'VIRGULA', 'ABRE_PAR', 'FECHA_PAR'
)

# Palavras reservadas para não confundir com nomes de jogadores
reserved = {
    'TIME': 'TIME',
    'FORMACAO': 'FORMACAO',
    'VALIDAR': 'VALIDAR',
    'GOL': 'POSICAO',
    'DEF': 'POSICAO',
    'MEI': 'POSICAO',
    'ATA': 'POSICAO'
}

# Expressões Regulares para tokens simples
t_DOIS_PONTOS = r':'
t_VIRGULA = r','
t_ABRE_PAR = r'\('
t_FECHA_PAR = r'\)'

# Ignorar espaços e tabs
t_ignore = " \t"

# Regex para identificar a formação tática (Ex: 4-4-2)
def t_CODIGO_FORMACAO(t):
    r'\d-\d-\d(-\d)?'
    return t

# Regex para nomes (jogadores ou time)
def t_NOME(t):
    r'[a-zA-Z_\u00C0-\u00FF][a-zA-Z0-9_\-\u00C0-\u00FF]*'
    # Verifica se é uma palavra reservada (TIME, GOL, etc.)
    t.type = reserved.get(t.value, 'NOME') 
    return t

# Regex para números (camisa)
def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Constrói o lexer
lexer = lex.lex()

# -----------------------------------------------------------------------------
# 2. ESTRUTURA DE DADOS (MEMÓRIA SEMÂNTICA)
# Onde guardamos o estado do time enquanto lemos o arquivo
# -----------------------------------------------------------------------------

dados_time = {
    'nome': None,
    'formacao': None, # Vai guardar [4, 4, 2]
    'elenco': {'GOL': [], 'DEF': [], 'MEI': [], 'ATA': []},
    'camisas_usadas': []
}

def limpar_dados():
    dados_time['nome'] = None
    dados_time['formacao'] = None
    dados_time['elenco'] = {'GOL': [], 'DEF': [], 'MEI': [], 'ATA': []}
    dados_time['camisas_usadas'] = []

# -----------------------------------------------------------------------------
# 3. ANÁLISE SINTÁTICA E SEMÂNTICA
# Regras gramaticais e ações de validação
# -----------------------------------------------------------------------------


def p_statement_list(p):
    '''statement : statement command
                 | command'''
    pass

def p_nome_composto_simples(p):
    'nome_composto : NOME'
    p[0] = p[1]

def p_nome_composto_recursivo(p):
    'nome_composto : nome_composto NOME'
    # Pega o nome acumulado (p[1]) e junta com o novo (p[2]) usando espaço
    p[0] = f"{p[1]} {p[2]}"

# Comando 1: Definir Nome do Time
def p_command_time(p):
    'command : TIME nome_composto'
    dados_time['nome'] = p[2]
    print(f"-> Time definido: {p[2]}")

# Comando 2: Definir Formação (Ação Semântica: Parsear a string "4-4-2")
def p_command_formacao(p):
    'command : FORMACAO CODIGO_FORMACAO'
    # Transforma "4-4-2" em uma lista de inteiros [4, 4, 2]
    partes = p[2].split('-') 
    dados_time['formacao'] = [int(x) for x in partes] 
    print(f"-> Formação definida: {p[2]}")

# Comando 3: Lista de Jogadores por Posição
def p_command_posicao(p):
    'command : POSICAO DOIS_PONTOS lista_jogadores'
    posicao = p[1] # Ex: DEF
    lista = p[3]   # Lista retornada por p_lista_jogadores
    
    # Ação Semântica: Guardar na estrutura
    dados_time['elenco'][posicao].extend(lista)
    
    # Ação Semântica: Registrar números de camisa para checar duplicidade depois
    for num, nome in lista:
        dados_time['camisas_usadas'].append(num)

# Regra Auxiliar: Lista Recursiva de Jogadores
# Ex: 1 (Rossi), 2 (Varela)
def p_lista_jogadores(p):
    '''lista_jogadores : jogador
                       | jogador VIRGULA lista_jogadores'''
    if len(p) == 2:
        p[0] = [p[1]] # Retorna lista com 1 jogador
    else:
        p[0] = [p[1]] + p[3] # Concatena jogador atual com o resto da lista

# Regra Auxiliar: Estrutura de um único jogador
# Ex: 1 (Rossi)
def p_jogador(p):
    'jogador : NUMERO ABRE_PAR nome_composto FECHA_PAR'
    p[0] = (p[1], p[3]) # Retorna tupla (Numero, Nome)

# Comando 4: VALIDAR (Aqui acontece a mágica Semântica pedida no trabalho)
def p_command_validar(p):
    'command : VALIDAR'
    print("\n--- INICIANDO VALIDAÇÃO SEMÂNTICA ---")
    
    erros = []
    
    # 1. Validação: Existe formação definida?
    fmt = dados_time['formacao']
    if not fmt:
        print("ERRO FATAL: Formação não definida.")
        return

    # 2. Validação: Contagem por setor vs Formação (Ex: 4-4-2)
    # fmt[0] = defensores, fmt[1] = meias, fmt[2] = atacantes
    qtd_def = len(dados_time['elenco']['DEF'])
    qtd_mei = len(dados_time['elenco']['MEI'])
    qtd_ata = len(dados_time['elenco']['ATA'])
    qtd_gol = len(dados_time['elenco']['GOL'])

# Lógica flexível para 3 ou 4 números
    # fmt é a lista, ex: [4, 4, 2] ou [4, 2, 3, 1]
    
    # DEFESA: Sempre o primeiro número
    if qtd_def != fmt[0]:
        erros.append(f"Erro Tático (DEF): Formação pede {fmt[0]}, escalados {qtd_def}.")

    # ATAQUE: Sempre o último número
    if qtd_ata != fmt[-1]: # -1 pega o último elemento da lista
        erros.append(f"Erro Tático (ATA): Formação pede {fmt[-1]}, escalados {qtd_ata}.")

    # MEIO-CAMPO: Soma de tudo que está entre o primeiro e o último
    # Se for 4-4-2: meio é [4] -> soma 4
    # Se for 4-2-3-1: meio é [2, 3] -> soma 5
    meios_necessarios = sum(fmt[1:-1]) 
    
    if qtd_mei != meios_necessarios:
        if len(fmt) == 4:
            detalhe = f"({fmt[1]}+{fmt[2]})"
        else:
            detalhe = ""
        erros.append(f"Erro Tático (MEI): Formação pede {meios_necessarios} {detalhe}, escalados {qtd_mei}.")
    # 3. Validação: Total de Jogadores
    total = qtd_gol + qtd_def + qtd_mei + qtd_ata
    if total != 11:
        erros.append(f"Erro Regulamento: O time tem {total} jogadores. É necessário ter exatamente 11.")

    # 4. Validação: Camisas Duplicadas
    camisas = dados_time['camisas_usadas']
    if len(camisas) != len(set(camisas)):
        from collections import Counter
        duplicadas = [item for item, count in Counter(camisas).items() if count > 1]
        erros.append(f"Erro Numeração: Existem camisas duplicadas no time: {duplicadas}")

    # Resultado Final
    if not erros:
        print(f"SUCESSO! O time {dados_time['nome']} está escalado corretamente no esquema {fmt}.")
        [print(f"  {pos}: {len(lst)} jogadores") for pos, lst in dados_time['elenco'].items()]
    else:
        print("FALHA NA VALIDAÇÃO:")
        for e in erros:
            print(f"  [X] {e}")
    
    # Limpa para o próximo input
    limpar_dados()

def p_error(p):
    if p:
        print(f"Erro de sintaxe no token '{p.value}'")
    else:
        print("Erro de sintaxe no final do arquivo")

# Build the parser
parser = yacc.yacc()

# -----------------------------------------------------------------------------
# EXECUÇÃO INTERATIVA
# -----------------------------------------------------------------------------
print("Analista Tático v1.0 (Digite as linhas do time e termine com VALIDAR)")
print("Exemplo:\nTIME Fla\nFORMACAO 4-4-2\nGOL: 1(Rossi)\nDEF: 2(Varela), 3(Leo)\nVALIDAR\n")

buffer_texto = ""
while True:
    try:
        s = input('tatica > ')
    except EOFError:
        break
    if not s: continue
    
    # Acumula as linhas até encontrar "VALIDAR" para processar o bloco (opcional, 
    # mas facilita colar o texto inteiro) ou processa linha a linha se a gramática permitir.
    # Como nossa gramática aceita 'statement command', podemos passar linha a linha.
    parser.parse(s)