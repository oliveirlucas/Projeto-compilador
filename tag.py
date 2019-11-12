from enum import Enum

class Tag(Enum):
   
   #Uma representacao em constante de todos os nomes 
   #de tokens para a linguagem.
   

   # Fim de arquivo
   EOF = -1

   # Palavras-chave
   KW_IF = 1
   KW_ELSE = 2
   KW_THEN = 3
   KW_PRINT = 4
   KW_END = 5
   KW_CLASS = 6
   KW_DEF = 7
   KW_RETURN = 8
   KW_DEFSTATIC = 9
   KW_VOID = 10
   KW_MAIN = 11
   KW_BOOL = 12
   KW_INTEGER = 13
   KW_STRING = 14
   KW_DOUBLE = 15
   KW_WHILE = 16
   KW_WRITE = 17
   KW_TRUE = 18
   KW_FALSE = 19


   # Operadores 
   OP_MENOR = 21
   OP_MENOR_IGUAL = 22
   OP_MAIOR_IGUAL = 23
   OP_MAIOR = 24
   OP_IGUAL = 25
   OP_DIFERENTE = 26
   OP_OR = 27
   OP_AND = 28
   OP_DIV = 29
   OP_MULT = 30
   OP_ATRIBUI = 31
   OP_SOMA = 32
   OP_SUBTRAI = 33
   OP_UNARIO = 54
   OP_NEGACAO = 55

   # Identificador
   ID = 34

   # Numeros
   CONST_INT = 35
   CONST_DOUBLE = 36

   # simbolos

   SIMB_DOIS_PONTOS = 45
   SIMB_PONTO = 46
   SIMB_PONTO_VIRGULA = 47
   SIMB_ABRE_PARENTESES = 48
   SIMB_FECHA_PARENTESES = 49
   SIMB_VIRGULA = 50
   SIMB_ABRE_COLCHETES = 51
   SIMB_FECHA_COLCHETES = 52

   #CONST_STRING

   CONST_STRING = 53
