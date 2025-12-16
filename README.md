

# Código da árvore:
TIME Flamengo ; Fluminense ; Sao Paulo FC
FORMACAO 4-4-2 ; 4-2-3-1 ; 4-4-2
GOL: 1(Rossi) ; 1(Fabio) ; 1 (Rafael)
DEF: 2(Varela),3(Leo),4(Ortiz),6(Ayrton) ; 2(Xavier),3(Thiago),4(Manoel),6(Marcelo) ; 13 (Rafinha), 5 (Arboleda), 4 (Alan Franco), 6 (Welington)
MEI: 5(Pulgar),8(Gerson),7(Luiz),14(Arrascaeta) ; 8(Martinelli),5(Andre),10(Ganso),20(Renato),11(Keno) ; 27 (Alisson), 29 (Pablo Maia), 7 (Lucas Moura), 10 (Luciano)
ATA: 9(Pedro),27(BH) ; 9(Cano) ; 33 (Erick), 9 (Calleri)
VALIDAR



------------------------------------

# Códigos para Teste
TIME Flamengo ; Fluminense
FORMACAO 4-4-2 ; 4-2-3-1
GOL: 1(Rossi) ; 1(Fabio)
DEF: 2(Varela),3(Leo),4(Ortiz),6(Ayrton) ; 2(Xavier),3(Thiago),4(Manoel),6(Marcelo)
MEI: 5(Pulgar),8(Gerson),7(Luiz),14(Arrascaeta) ; 8(Martinelli),5(Andre),10(Ganso),20(Renato),11(Keno)
ATA: 9(Pedro),27(BH) ; 9(Cano)
VALIDAR


## Código com 4 Times
TIME Flamengo ; Fluminense ; Vasco ; Sao Paulo FC
FORMACAO 4-4-2 ; 4-2-3-1 ; 4-4-2 ; 4-4-2
GOL: 1(Rossi) ; 1(Fabio) ; 1 (Rafael) ; 1 (Rafael)
DEF: 2(Varela),3(Leo),4(Ortiz),6(Ayrton) ; 2(Xavier),3(Thiago),4(Manoel),6(Marcelo) ; 13 (Rafinha), 5 (Arboleda), 4 (Alan Franco), 6 (Welington) ; 13 (Rafinha), 5 (Arboleda), 4 (Alan Franco), 6 (Welington)
MEI: 5(Pulgar),8(Gerson),7(Luiz),14(Arrascaeta) ; 8(Martinelli),5(Andre),10(Ganso),20(Renato),11(Keno) ; 27 (Alisson), 29 (Pablo Maia), 7 (Lucas Moura), 10 (Luciano) ; 27 (Alisson), 29 (Pablo Maia), 7 (Lucas Moura), 10 (Luciano)
ATA: 9(Pedro),27(BH) ; 9(Cano) ; 33 (Erick), 9 (Calleri) ; 33 (Erick), 9 (Calleri)
VALIDAR

## Código que dá erro
### Jogador Faltando no Flamengo
TIME Flamengo ; Fluminense
FORMACAO 4-4-2 ; 4-2-3-1
GOL: 1(Rossi) ; 1(Fabio)
DEF: 2(Varela),3(Leo),4(Ortiz),6(Ayrton) ; 2(Xavier),3(Thiago),4(Manoel),6(Marcelo)
MEI: 5(Pulgar),8(Gerson),7(Luiz),14(Arrascaeta) ; 8(Martinelli),5(Andre),10(Ganso),20(Renato),11(Keno)
ATA: 9(Pedro) ; 9(Cano)
VALIDAR

### Jogador com número repetido
TIME Flamengo ; Fluminense
FORMACAO 4-4-2 ; 4-2-3-1
GOL: 1(Rossi) ; 1(Fabio)
DEF: 2(Varela),3(Leo),4(Ortiz),6(Ayrton) ; 2(Xavier),3(Thiago),4(Manoel),6(Marcelo)
MEI: 5(Pulgar),9(Gerson),7(Luiz),14(Arrascaeta) ; 8(Martinelli),5(Andre),9(Ganso),20(Renato),11(Keno)
ATA: 9(Pedro) ; 9(Cano)
VALIDAR

## Código com 1 time
TIME Flamengo Moderno
FORMACAO 4-2-3-1
GOL: 1 (Rossi)
DEF: 2 (Varela), 3 (Ortiz), 4 (Leo), 6 (Ayrton)
MEI: 8 (Gerson), 5 (Pulgar), 14 (Arrascaeta), 7 (Luiz), 11 (Cebolinha)
ATA: 9 (Pedro)
VALIDAR

TIME Sao Paulo FC
FORMACAO 4-4-2
GOL: 1 (Rafael)
DEF: 13 (Rafinha), 5 (Arboleda), 4 (Alan Franco), 6 (Welington)
MEI: 27 (Alisson), 29 (Pablo Maia), 7 (Lucas Moura), 10 (Luciano)
ATA: 33 (Erick), 9 (Calleri)
VALIDAR