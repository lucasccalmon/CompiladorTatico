import ply.lex as lex
import ply.yacc as yacc
import json
import sys

# -----------------------------------------------------------------------------
# 1. ANÁLISE LÉXICA
# -----------------------------------------------------------------------------
tokens = (
    'TIME', 'FORMACAO', 'VALIDAR', 'STOP',
    'POSICAO', 
    'CODIGO_FORMACAO',
    'NUMERO', 'NOME',
    'DOIS_PONTOS', 'VIRGULA', 'ABRE_PAR', 'FECHA_PAR',
    'PONTO_VIRGULA'
)

reserved = {
    'TIME': 'TIME', 'FORMACAO': 'FORMACAO', 'VALIDAR': 'VALIDAR', 'STOP': 'STOP',
    'GOL': 'POSICAO', 'DEF': 'POSICAO', 'MEI': 'POSICAO', 'ATA': 'POSICAO'
}

t_DOIS_PONTOS = r':'
t_VIRGULA = r','
t_PONTO_VIRGULA = r';'
t_ABRE_PAR = r'\('
t_FECHA_PAR = r'\)'
t_ignore = " \t"

def t_CODIGO_FORMACAO(t):
    r'\d+-\d+-\d+(-\d+)?'
    return t

def t_NOME(t):
    r'[a-zA-Z_\u00C0-\u00FF][a-zA-Z0-9_\-\u00C0-\u00FF]*'
    t.type = reserved.get(t.value, 'NOME') 
    return t

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

lexer = lex.lex()

# -----------------------------------------------------------------------------
# 2. ESTRUTURA DE DADOS (LISTA DINÂMICA)
# -----------------------------------------------------------------------------

# Nossa memória agora é uma lista de objetos de times
teams_db = []

def criar_time(nome):
    return {
        'nome': nome,
        'formacao': None,
        'elenco': {'GOL': [], 'DEF': [], 'MEI': [], 'ATA': []},
        'camisas_usadas': []
    }

def limpar_dados():
    global teams_db
    teams_db = []

# -----------------------------------------------------------------------------
# 3. ANÁLISE SINTÁTICA (GRAMÁTICA RECURSIVA PARA LISTAS)
# -----------------------------------------------------------------------------

def p_statement_list(p):
    '''statement : statement command
                 | command'''
    pass

def p_command_stop(p):
    'command : STOP'
    print("\nEncerrando Compilador... Até logo!")
    sys.exit()

# --- REGRAS AUXILIARES DE NOMES ---
def p_nome_composto_simples(p):
    'nome_composto : NOME'
    p[0] = p[1]

def p_nome_composto_recursivo(p):
    'nome_composto : nome_composto NOME'
    p[0] = f"{p[1]} {p[2]}"

# --- REGRAS DE "SUPER LISTAS" (Separadas por ;) ---

# 1. Lista de Nomes de Times (Ex: Fla ; Flu ; Vasco)
def p_lista_nomes_times_single(p):
    'lista_nomes_times : nome_composto'
    p[0] = [p[1]] # Retorna lista com 1 nome

def p_lista_nomes_times_multi(p):
    'lista_nomes_times : lista_nomes_times PONTO_VIRGULA nome_composto'
    p[0] = p[1] + [p[3]] # Adiciona novo nome à lista existente

# 2. Lista de Formações (Ex: 4-4-2 ; 4-3-3 ; 3-5-2)
def p_lista_formacoes_single(p):
    'lista_formacoes : CODIGO_FORMACAO'
    p[0] = [p[1]]

def p_lista_formacoes_multi(p):
    'lista_formacoes : lista_formacoes PONTO_VIRGULA CODIGO_FORMACAO'
    p[0] = p[1] + [p[3]]

# 3. Lista de Listas de Jogadores (Ex: [Rossi] ; [Fabio] ; [Leo])
# Aqui temos uma lista (separada por ;) de listas (separadas por ,)
def p_super_lista_jogadores_single(p):
    'super_lista_jogadores : lista_jogadores'
    p[0] = [p[1]] # Retorna [[(1, Rossi), (2, Varela)]]

def p_super_lista_jogadores_multi(p):
    'super_lista_jogadores : super_lista_jogadores PONTO_VIRGULA lista_jogadores'
    p[0] = p[1] + [p[3]] # Concatena a nova lista de jogadores

# Regra base de lista de jogadores (Separada por vírgula)
def p_lista_jogadores(p):
    '''lista_jogadores : jogador
                       | jogador VIRGULA lista_jogadores'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_jogador(p):
    'jogador : NUMERO ABRE_PAR nome_composto FECHA_PAR'
    p[0] = (p[1], p[3])

# --- COMANDOS PRINCIPAIS ---

# Comando TIME: Inicializa N times
def p_command_time(p):
    'command : TIME lista_nomes_times'
    global teams_db
    names = p[2] # Recebe lista ['Fla', 'Flu', 'Vasco']
    
    teams_db = [] # Reseta DB
    for n in names:
        teams_db.append(criar_time(n))
        
    print(f"-> Inicializando {len(teams_db)} times: {', '.join(names)}")

# Comando FORMACAO: Distribui táticas para os N times
def p_command_formacao(p):
    'command : FORMACAO lista_formacoes'
    codes = p[2] # Recebe lista ['4-4-2', '4-3-3'...]
    
    if len(codes) != len(teams_db):
        print(f"ERRO SEMÂNTICO: Você definiu {len(teams_db)} times, mas forneceu {len(codes)} formações.")
        return

    for i, code in enumerate(codes):
        partes = code.split('-')
        teams_db[i]['formacao'] = [int(x) for x in partes]
    
    print(f"-> Táticas atribuídas para {len(teams_db)} times.")

# Comando POSICAO: Distribui jogadores para os N times
def p_command_posicao(p):
    'command : POSICAO DOIS_PONTOS super_lista_jogadores'
    posicao = p[1] # GOL, DEF...
    listas_recebidas = p[3] # Lista de listas
    
    if len(listas_recebidas) != len(teams_db):
        print(f"ERRO SEMÂNTICO ({posicao}): Esperado dados para {len(teams_db)} times, recebido para {len(listas_recebidas)}.")
        return

    # Distribui cada lista para seu respectivo time
    for i, lista_jogadores in enumerate(listas_recebidas):
        time_atual = teams_db[i]
        time_atual['elenco'][posicao].extend(lista_jogadores)
        for num, nome in lista_jogadores:
            time_atual['camisas_usadas'].append(num)

# --- VALIDAÇÃO E TRADUÇÃO ---

def validar_unico(dados):
    erros = []
    fmt = dados['formacao']
    nome = dados['nome']
    
    if not fmt:
        return [f"Time {nome}: Formação não definida"]

    qtd_gol = len(dados['elenco']['GOL'])
    qtd_def = len(dados['elenco']['DEF'])
    qtd_mei = len(dados['elenco']['MEI'])
    qtd_ata = len(dados['elenco']['ATA'])
    
    meios_nec = sum(fmt[1:-1])

    if qtd_gol != 1: erros.append(f"{nome} (GOL): Tem {qtd_gol}, precisa 1")
    if qtd_def != fmt[0]: erros.append(f"{nome} (DEF): Tem {qtd_def}, precisa {fmt[0]}")
    if qtd_mei != meios_nec: erros.append(f"{nome} (MEI): Tem {qtd_mei}, precisa {meios_nec}")
    if qtd_ata != fmt[-1]: erros.append(f"{nome} (ATA): Tem {qtd_ata}, precisa {fmt[-1]}")

    total = qtd_gol + qtd_def + qtd_mei + qtd_ata
    if total != 11: erros.append(f"{nome} (TOTAL): Tem {total} jogadores, precisa 11")

    camisas = dados['camisas_usadas']
    if len(camisas) != len(set(camisas)):
        erros.append(f"{nome}: Numeração duplicada")

    return erros

def p_command_validar(p):
    'command : VALIDAR'
    
    if not teams_db:
        print("Aviso: Nenhum time para validar.")
        return

    print(f"\n--- PROCESSANDO {len(teams_db)} TIMES ---")
    
    todos_erros = []
    
    # 1. Validação em Lote
    for time in teams_db:
        erros_time = validar_unico(time)
        todos_erros.extend(erros_time)
    
    if todos_erros:
        print("ERROS DE COMPILAÇÃO ENCONTRADOS:")
        for e in todos_erros:
            print(f" [X] {e}")
        print("Falha na tradução. Corrija os erros acima.")
    else:
        # 2. Tradução para JSON (Formato Campeonato)
        print("Validação OK! Gerando saída traduzida (JSON)...\n")
        
        torneio_output = {
            "tournament_data": {
                "total_teams": len(teams_db),
                "teams": []
            }
        }
        
        for time in teams_db:
            team_obj = {
                "name": time['nome'],
                "strategy": "-".join(map(str, time['formacao'])),
                "roster": time['elenco']
            }
            torneio_output["tournament_data"]["teams"].append(team_obj)
            
        print(json.dumps(torneio_output, indent=4, ensure_ascii=False))
        print("\n--- FIM DA TRADUÇÃO ---")
    
    limpar_dados()

def p_error(p):
    if p: print(f"Erro de sintaxe no token '{p.value}'")
    else: print("Erro no fim do arquivo")

parser = yacc.yacc()

# -----------------------------------------------------------------------------
# LOOP PRINCIPAL
# -----------------------------------------------------------------------------
print("Compilador de Campeonatos v3.0 (Multi-Times)")
print("Sintaxe: DADOS_TIME_1 ; DADOS_TIME_2 ; DADOS_TIME_3 ...")
print("Digite STOP para sair.")

while True:
    try:
        s = input('>>> ')
    except EOFError:
        break
    if not s: continue
    parser.parse(s)