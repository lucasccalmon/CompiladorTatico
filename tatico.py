import ply.lex as lex
import ply.yacc as yacc
import json
import sys

# -----------------------------------------------------------------------------
# 1. ANÁLISE LÉXICA
# Definição dos tokens que nossa linguagem entende
# -----------------------------------------------------------------------------

tokens = (
    'TIME', 'FORMACAO', 'VALIDAR', 'STOP',
    'POSICAO',  # GOL, DEF, MEI, ATA
    'CODIGO_FORMACAO', # Ex: 4-4-2, 4-3-3
    'NUMERO', 'NOME',
    'DOIS_PONTOS', 'VIRGULA', 'ABRE_PAR', 'FECHA_PAR',
    'PONTO_VIRGULA'
)

# Palavras reservadas para não confundir com nomes de jogadores
reserved = {
    'TIME': 'TIME',
    'FORMACAO': 'FORMACAO',
    'VALIDAR': 'VALIDAR',
    'STOP':'STOP',
    'GOL': 'POSICAO',
    'DEF': 'POSICAO',
    'MEI': 'POSICAO',
    'ATA': 'POSICAO'
}

# Expressões Regulares para tokens simples
t_DOIS_PONTOS = r':'
t_VIRGULA = r','
t_PONTO_VIRGULA = r';'
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

# Função auxiliar para criar um time vazio
def novo_time_struct():
    return {
        'ativo': False, # Flag para saber se este time está sendo usado
        'nome': None,
        'formacao': None,
        'elenco': {'GOL': [], 'DEF': [], 'MEI': [], 'ATA': []},
        'camisas_usadas': []
    }

# Memória Global
match_data = {
    'casa': novo_time_struct(),
    'fora': novo_time_struct()
}

def limpar_dados():
    match_data['casa'] = novo_time_struct()
    match_data['fora'] = novo_time_struct()

# -----------------------------------------------------------------------------
# 3. ANÁLISE SINTÁTICA E SEMÂNTICA
# Regras gramaticais e ações de validação
# -----------------------------------------------------------------------------


def p_statement_list(p):
    '''statement : statement command
                 | command'''
    pass

# --- NOVA REGRA DO STOP ---
def p_command_stop(p):
    'command : STOP'
    print("\nEncerrando Analisador Tático... Até logo!")
    sys.exit() # Encerra o script Python

def p_nome_composto_simples(p):
    'nome_composto : NOME'
    p[0] = p[1]

def p_nome_composto_recursivo(p):
    'nome_composto : nome_composto NOME'
    # Pega o nome acumulado (p[1]) e junta com o novo (p[2]) usando espaço
    p[0] = f"{p[1]} {p[2]}"

# Comando 1: Definir Nome do Time
def p_command_time_simples(p):
    'command : TIME nome_composto'
    match_data['casa']['nome'] = p[2]
    match_data['casa']['ativo'] = True
    # Garante que o "fora" está desligado
    match_data['fora']['ativo'] = False 
    print(f"-> Time definido: {p[2]}")

def p_command_time_duplo(p):
    'command : TIME nome_composto PONTO_VIRGULA nome_composto'
    match_data['casa']['nome'] = p[2]
    match_data['casa']['ativo'] = True
    match_data['fora']['nome'] = p[4]
    match_data['fora']['ativo'] = True
    print(f"-> Confronto definido: {p[2]} (Casa) vs {p[4]} (Fora)")

# Comando 2: Definir Formação (Ação Semântica: Parsear a string "4-4-2")
def p_command_formacao_simples(p):
    'command : FORMACAO CODIGO_FORMACAO'
    partes = p[2].split('-')
    match_data['casa']['formacao'] = [int(x) for x in partes]
    print(f"-> Tática: {p[2]}")
    
def p_command_formacao_duplo(p):
    'command : FORMACAO CODIGO_FORMACAO PONTO_VIRGULA CODIGO_FORMACAO'
    # Casa
    partes_casa = p[2].split('-')
    match_data['casa']['formacao'] = [int(x) for x in partes_casa]
    # Fora
    partes_fora = p[4].split('-')
    match_data['fora']['formacao'] = [int(x) for x in partes_fora]
    print(f"-> Táticas: {p[2]} vs {p[4]}")


def processar_lista(lista, time_key, posicao):
    if not lista: return
    match_data[time_key]['elenco'][posicao].extend(lista)
    for num, nome in lista:
        match_data[time_key]['camisas_usadas'].append(num)

# Comando 3: Lista de Jogadores por Posição
def p_command_posicao_simples(p):
    'command : POSICAO DOIS_PONTOS lista_jogadores'
    processar_lista(p[3], 'casa', p[1])

def p_command_posicao_duplo(p):
    'command : POSICAO DOIS_PONTOS lista_jogadores PONTO_VIRGULA lista_jogadores'
    processar_lista(p[3], 'casa', p[1])
    processar_lista(p[5], 'fora', p[1])

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
def validar_time(dados, label):
    # Se o time não estiver marcado como ativo, ignoramos (não é erro)
    if not dados['ativo']: 
        return True 
        
    print(f"\n--- Validando {label}: {dados['nome']} ---")
    erros = []
    fmt = dados['formacao']
    
    if not fmt:
        print(f"ERRO: Formação não definida para {label}.")
        return False

    qtd_def = len(dados['elenco']['DEF'])
    qtd_mei = len(dados['elenco']['MEI'])
    qtd_ata = len(dados['elenco']['ATA'])
    qtd_gol = len(dados['elenco']['GOL'])
    
    meios_necessarios = sum(fmt[1:-1])

    if qtd_gol != 1: erros.append(f"Goleiros: Esperado 1, achou {qtd_gol}")
    if qtd_def != fmt[0]: erros.append(f"Defesa: Esperado {fmt[0]}, achou {qtd_def}")
    if qtd_mei != meios_necessarios: erros.append(f"Meio: Esperado {meios_necessarios}, achou {qtd_mei}")
    if qtd_ata != fmt[-1]: erros.append(f"Ataque: Esperado {fmt[-1]}, achou {qtd_ata}")

    total = qtd_gol + qtd_def + qtd_mei + qtd_ata
    if total != 11: erros.append(f"Total: Time tem {total} jogadores (precisa de 11)")

    camisas = dados['camisas_usadas']
    if len(camisas) != len(set(camisas)):
        erros.append("Numeração duplicada detectada")

    if not erros:
        print("-> OK! Time válido.")
        return True
    else:
        for e in erros: print(f"-> [X] {e}")
        return False

def p_command_validar(p):
    'command : VALIDAR'
    
    # --- ETAPA 1: VALIDAÇÃO (O que você já tinha) ---
    erros = []
    
    # Valida Casa
    # Suponha que as variáveis ok_casa e ok_fora já foram calculadas usando sua lógica anterior
    ok_casa = validar_time(match_data['casa'], "Casa")
    
    ok_fora = True
    if match_data['fora']['ativo']:
        ok_fora = validar_time(match_data['fora'], "Fora")
    
    # --- ETAPA 2: GERAÇÃO DE CÓDIGO (A TRADUÇÃO) ---
    # Se não houver erros, nós TRADUZIMOS a entrada para JSON
    if ok_casa and ok_fora:
        print("\n--- INÍCIO DA TRADUÇÃO (OUTPUT) ---\n")
        
        # Montamos o objeto final de saída (A estrutura transformada)
        saida_compilada = {
            "match_event": {
                "home_team": {
                    "name": match_data['casa']['nome'],
                    "formation_scheme": "-".join(map(str, match_data['casa']['formacao'])),
                    "squad": match_data['casa']['elenco']
                }
            }
        }

        # Se tiver time de fora, adiciona ao JSON
        if match_data['fora']['ativo']:
            saida_compilada["match_event"]["away_team"] = {
                "name": match_data['fora']['nome'],
                "formation_scheme": "-".join(map(str, match_data['fora']['formacao'])),
                "squad": match_data['fora']['elenco']
            }

        # Imprime o JSON formatado
        # Isso é equivalente a gerar o código de montagem ou resultado final
        json_output = json.dumps(saida_compilada, indent=4, ensure_ascii=False)
        print(json_output)
        
        print("\n--- FIM DA TRADUÇÃO ---")
        
    else:
        print("ERRO DE COMPILAÇÃO: As regras semânticas foram violadas.")
    
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