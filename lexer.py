import sys

from ts import TS
from tag import Tag
from token import Token

class Lexer():
   
   #Classe que representa o Lexer:
   
   #[1] Voce devera se preocupar quando incremetar as linhas e colunas,
   #assim como quando decrementar ou reinicia-las. Lembre-se, ambas 
   #comecam em 1.
   #[2] Toda vez que voce encontrar um lexema completo, voce deve retornar
   #um objeto Token(Tag, "lexema", linha, coluna). Cuidado com as
   #palavras reservadas, que ja sao cadastradas na TS. Essa consulta
   #voce devera fazer somente quando encontrar um Identificador.
   #[3] Se o caractere lido nao casar com nenhum caractere esperado,
   #vapresentar a mensagem de erro na linha e coluna correspondente.
   #Obs.: lembre-se de usar o metodo retornaPonteiro() quando necessario. 
   #      lembre-se de usar o metodo sinalizaErroLexico() para mostrar
   #      a ocorrencia de um erro lexico.
   
   def __init__(self, input_file):
      try:
         self.input_file = open(input_file, 'rb')
         self.lookahead = 0
         self.n_line = 1
         self.n_column = 1
         self.ts = TS()
      except IOError:
         print('Erro de abertura do arquivo. Encerrando.')
         sys.exit(0)

   def closeFile(self):
      try:
         self.input_file.close()
      except IOError:
         print('Erro ao fechar arquivo. Encerrando.')
         sys.exit(0)

   def sinalizaErroLexico(self, message):
      print("[Erro Lexico]: ", message, "\n")

   def retornaPonteiro(self):
      if(self.lookahead.decode('ascii') != ''):
         self.input_file.seek(self.input_file.tell()-1)
         self.n_column -= 1

   def printTS(self):
      self.ts.printTS()

   def proxToken(self):   
      estado = 1
      lexema = ""
      c = '\u0000'

      while(True):
         self.lookahead = self.input_file.read(1)
         c = self.lookahead.decode('ascii')

         if(estado == 1):#--------------Q0
            if(c == ''):
               return Token(Tag.EOF, "EOF", self.n_line, self.n_column)               
            elif(c == ' ' or c == '\t' or c == '\n' or c == '\r'):
               estado = 1
               if(c == '\n'):
                  self.n_line += 1
                  self.n_column = 1
               elif(c == ' ' or '\r'):
                  self.n_column += 1
               elif(c == '\t'):
                  self.n_column += 3
            elif(c == '#'):#--------------Q24
               estado = 24
               self.n_column += 1
            elif(c == '"'):#--------------Q21
               estado = 21
               self.n_column += 1
            elif(c == '='):#--------------Q1
               estado = 2
               self.n_column += 1
            elif(c == '!'):#--------------Q3
               estado = 4
               self.n_column += 1
            elif(c == '<'):#--------------Q6
               estado = 6
               self.n_column += 1
            elif(c == '>'):#--------------Q9
               estado = 9
               self.n_column += 1
            elif(c.isdigit()):#--------------Q16
               lexema += c
               estado = 16
               self.n_column += 1
            elif(c.isalpha()):#--------------Q26
               lexema += c
               estado = 26
               self.n_column += 1
            elif(c == '/'):#--------------Q15
               self.n_column += 1
               token = Token(Tag.OP_DIV, "/", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == '.'):#--------------Q30
               self.n_column += 1
               token = Token(Tag.SIMB_PONTO, ".", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == ']'):#--------------Q36
               self.n_column += 1
               token = Token(Tag.SIMB_FECHA_COLCHETES, "]", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == '['):#--------------Q35
               self.n_column += 1
               token = Token(Tag.SIMB_ABRE_COLCHETES, "[", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token            

            elif(c == ','):#--------------Q33
               self.n_column += 1
               token = Token(Tag.SIMB_VIRGULA, ",", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == ')'):#--------------Q34
               self.n_column += 1
               token = Token(Tag.SIMB_FECHA_PARENTESES, ")", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token

            elif(c == '('):#--------------Q32
               self.n_column += 1
               token = Token(Tag.SIMB_ABRE_PARENTESES, "(", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token

            elif(c == ';'):#--------------Q31
               self.n_column += 1
               token = Token(Tag.SIMB_PONTO_VIRGULA, ";", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == ':'):#--------------Q29
               self.n_column += 1
               token = Token(Tag.SIMB_DOIS_PONTOS, ":", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == '*'):#--------------Q14
               self.n_column += 1
               token = Token(Tag.OP_MULT, "*", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == '+'):#--------------Q13
               self.n_column += 1
               token = Token(Tag.OP_SOMA, "+", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            elif(c == '-'):#--------------Q12
               self.n_column += 1
               token = Token(Tag.OP_UNARIO, "-", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               

            else:
               self.sinalizaErroLexico("Caractere invalido [" + c + "] na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None
         elif(estado == 2):
            if(c == '='):#--------------Q2
               self.n_column += 1
               token = Token(Tag.OP_IGUAL, "==", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token
            else:#--------------Q28
               self.retornaPonteiro()
               token = Token(Tag.OP_ATRIBUI, "=", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token

         elif(estado == 4):
            if(c == '='):#--------------Q5
               self.n_column += 1
               token = Token(Tag.OP_DIFERENTE, "!=", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               
            else: #--------------Q4
               self.retornaPonteiro()
               token = Token(Tag.OP_UNARIO, "!", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)

               return token
         elif(estado == 6):
            if(c == '='):#--------------Q7
               self.n_column += 1
               token = Token(Tag.OP_MENOR_IGUAL, "<=", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               
            else:#--------------Q8
               self.retornaPonteiro()
               token = Token(Tag.OP_MENOR, "<", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)

               return token               
         elif(estado == 9):
            if(c == '='):#--------------Q10
               self.n_column += 1
               token = Token(Tag.OP_MAIOR_IGUAL, ">=", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token               
            else:#--------------Q11
               self.retornaPonteiro()
               token = Token(Tag.OP_MAIOR, ">", self.n_line, self.n_column)
               self.ts.addToken(lexema, token)

               return token         
         elif(estado == 16):
            if(c.isdigit()):#--------------Q16
               lexema += c 
               self.n_column += 1
            elif(c == '.'):#--------------Q18
               lexema += c 
               estado = 18
               self.n_column += 1
            elif(c == '-'):               
               #RECONHECER INT
               self.n_column += 1
               token = Token(Tag.CONST_INT, lexema, self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token
               #RECONHECER OPERADOR MENOS
              # token = Token(Tag.OP_SUBTRAI, lexema, self.n_line, self.n_column)
               #self.ts.addToken(lexema, token)
               #return token
            else:#--------------Q17
               self.retornaPonteiro()
               token = Token(Tag.CONST_INT, lexema, self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token
         elif(estado == 18):#---RECONHECER DOUBLE
            if(c.isdigit()):#--------------Q19
               lexema += c
               self.n_column += 1
            elif(c == '-'):
               #RECONHECER DOUBLE
               token = Token(Tag.CONST_DOUBLE, lexema, self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token
               #RECONHECER OPERADOR MENOS
               #token = Token(Tag.OP_SUBTRAI, lexema, self.n_line, self.n_column)
               #self.ts.addToken(lexema, token)
               #return token

            else:#--------------Q20
               self.retornaPonteiro()
               token = Token(Tag.CONST_DOUBLE, lexema, self.n_line, self.n_column)
               self.ts.addToken(lexema, token)
               return token

         elif(estado == 21):
            if(c == '"'):#--------------Q23
               self.n_column += 1
               return Token(Tag.CONST_STRING, lexema, self.n_line, self.n_column)

            elif(c == '\n'):
               self.sinalizaErroLexico("Só é permitido String de uma Linha! Erro na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               self.n_column = 1
               self.n_line += 1
            else:#--------------Q22
               lexema += c
               self.n_column += 1
         elif(estado == 24):
            if(c == '\n'):#--------------Q0
               self.n_line = self.n_line + 1
               self.n_column = 1
            else:#--------------Q25
               estado = 24
         elif(estado == 26):
            if(c.isalnum()):#--------------Q26
               lexema += c
               self.n_column += 1
            else:#--------------Q27
               self.retornaPonteiro()
               token = self.ts.getToken(lexema)
               if(token is None):#--------------VERIFICA TABELA
                  token = Token(Tag.ID, lexema, self.n_line, self.n_column)
                  self.ts.addToken(lexema, token)
               else:
                  token.setLinha(self.n_line)
                  token.setColuna(self.n_column)
               return token


         # [TAREFA] Completar a l
         # ogica para o cometario conforme o AFD.

         # fim if's de estados
      # fim while
