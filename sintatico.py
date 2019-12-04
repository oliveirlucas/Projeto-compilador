import sys

from ts import TS
from tag import Tag
from token import Token
from lexer import Lexer
from no import No

"""
 * *
 * [TODO]: tratar retorno 'None' do Lexer que esta sem Modo Panico
 *
 *
 * Modo Pânico do Parser: 
    * Para tomar a decisao de escolher uma das regras (quando mais de uma disponivel),
    * o parser usa incialmente o FIRST(), e para alguns casos, FOLLOW(). Essa informacao eh dada pela TP.
    * Caso nao existe a regra na TP que corresponda ao token da entrada,
    * informa-se uma mensagem de erro e inicia-se o Modo Panico:
    * [1] calcula-se o FOLLOW do NAO-TERMINAL (a esquerda) da regra atual: esse NAO-TERMINAL estara no topo da pilha;
    * [2] se o token da entrada estiver neste FOLLOW, desempilha-se o nao-terminal atual - metodo synch() - retorna da recursao;
    * [3] caso contrario, a entrada eh avancada para uma nova comparacao e mantem-se o nao-terminal no topo da pilha 
    * (se for a pilha recursiva, mantem o procedimento no topo da recursao) - metodo skip().
    * 
    * O Modo Panico encerra-se, 'automagicamente', quando um token esperado aparece.
    * Para NAO implementar o Modo Panico, basta sinalizar erro quando nao
    * for possivel utilizar alguma das regras. Em seguida, encerrar a execucao usando sys.exit(0).
"""

class Parser():

   def __init__(self, lexer):
      self.lexer = lexer
      self.token = lexer.proxToken() # Leitura inicial obrigatoria do primeiro SIMB

   def sinalizaErroSemantico(self, message):
      print("[Erro Semantico] na linha " + str(self.token.getLinha()) + " e coluna " + str(self.token.getColuna()) + ": ")
      print(message, "\n")

   def sinalizaErroSintatico(self, message):
      print("[Erro Sintatico] na linha " + str(self.token.getLinha()) + " e coluna " + str(self.token.getColuna()) + ": ")
      print(message, "\n")

   def advance(self):
      print("[DEBUG] token: ", self.token.toString())
      self.token = self.lexer.proxToken()
   
   def skip(self, message):
      self.sinalizaErroSintatico(message)
      self.advance()

   # verifica token esperado t 
   def eat(self, t):
      if(self.token.getNome() == t):
         self.advance()
         return True
      else:
         return False

   """
   LEMBRETE:
   Todas as decisoes do Parser, sao guiadas pela Tabela Preditiva (TP)
   """

   # Programa -> Classe EOF
   def Programa(self):
      self.Classe()
      if(self.token.getNome() != Tag.EOF):
         self.sinalizaErroSintatico("Esperado \"EOF\"; encontrado " + "\"" + self.token.getLexema() + "\"")
   
   # Classe ->  "class" ID ":" ListaFuncao  Main "end" "." 
   def Classe(self):
      if(self.eat(Tag.KW_CLASS)):
         
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" + "\""+ self.token.getLexema() + "\"")
         else:

         
         if(not self.eat(Tag.SIMB_DOIS_PONTOS)):
            self.sinalizaErroSintatico("Esperado\":\"; encontrado" + "\""+ self.token.getLexema() + "\"")        
         
         self.ListaFuncao()
         self.Main()
         
         if(not self.eat(Tag.KW_END)):
            self.sinalizaErroSintatico("Esperado\"end\"; encontrado " + "\""+ self.token.getLexema() + "\"")

         if(not self.eat(Tag.SIMB_PONTO)):
            self.sinalizaErroSintatico("Esperado\".\"; encontrado " + "\""+ self.token.getLexema() + "\"")

      # Synch: FOLLOW de Classe
      else:         
         if(self.token.getNome() == Tag.EOF):
            self.sinalizaErroSintatico("Esperado\"class\"; encontrado " + "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"class\"; encontrado " + "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Classe()
               

   # DeclaraID ->  TipoPrimitivo ID ";"
   def DeclareID(self):
      if(self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or self.token.getNome() == Tag.KW_STRING or self.token.getNome() == Tag.KW_DOUBLE or self.token.getNome() == Tag.KW_VOID):
         noTipoPrimitivo = self.TipoPrimitivo()

         tempToken = copy.copy(self.token)
         
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         else:
            self.lexer.ts.setTipo(tempToken.getLexema(), noTipoPrimitivo.getTipo())  

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      # Synch: FOLLOW de DeclareID
      else:
         if(self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or self.token.getNome() == Tag.KW_STRING or self.token.getNome() == Tag.KW_DOUBLE or self.token.getNome() == Tag.KW_VOID or self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END):
            self.sinalizaErroSintatico("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.DeclareID()
   
   # ListaFuncao -> ListaFuncao’ 
   def ListaFuncao(self):
      if(self.token.getNome() == Tag.KW_DEF or self.token.getNome() == Tag.KW_DEFSTATIC):
         self.ListaFuncaoLinha()

      # SKIP somente por causa do vazio
      else:
            self.skip("Esperado\"def ou defstatic\"; encontrado" + "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.ListaFuncao()

   # ListaFuncao’ -> Funcao ListaFuncao’ | ε 
   def ListaFuncaoLinha(self):
      if(self.token.getNome() == Tag.KW_DEF):
         self.Funcao()
      
         self.ListaFuncaoLinha()
      
      elif(self.token.getNome() == Tag.KW_DEFSTATIC):
         return

      # SKIP somente por causa do vazio
      else:
            self.skip("Esperado\"def ou ε\"; encontrado" + "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.ListaFuncaoLinha()

   # Funcao ->"def" TipoPrimitivo ID "(" ListaArg ")" ":" RegexDeclaraId ListaCmd Retorno "end" ";" 
   def Funcao(self):
      if(self.eat(Tag.KW_DEF)):
         #self.sinalizaErroSintatico("Esperado\"def\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         self.TipoPrimitivo()

         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_ABRE_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.ListaArg()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_DOIS_PONTOS)):
            self.sinalizaErroSintatico("Esperado\":\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.RegexDeclaraId()
         self.ListaCmd()

         noRetorno = self.Retorno()
         if(noRetorno)

         if(not self.eat(Tag.KW_END)):
            self.sinalizaErroSintatico("Esperado\"end\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      # Synch: FOLLOW de Funcao
      else:
         if(self.token.getNome() == Tag.KW_DEF or self.token.getNome() == Tag.KW_DEFSTATIC):
            self.sinalizaErroSintatico("Esperado\"def\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"def\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Funcao()
   
   # RegexDeclaraId -> DeclaraID RegexDeclaraId | ε 
   def RegexDeclaraId(self):
      if(self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or self.token.getNome() == Tag.KW_STRING or self.token.getNome() == Tag.KW_DOUBLE or self.token.getNome() == Tag.KW_VOID):
         self.DeclareID()

         self.RegexDeclaraId()
      
      elif(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END):
         return

      else:
            self.skip("Esperado\"bool, interger, String, double, void | ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.RegexDeclaraId()

   # ListaArg → Arg ListaArg’
   def ListaArg(self):
      if(self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or self.token.getNome() == Tag.KW_STRING or self.token.getNome() == Tag.KW_DOUBLE or self.token.getNome() == Tag.KW_VOID):
         self.Arg()

         self.ListaArgLinha()

      # Synch: FOLLOW de ListaArg
      else:
         if(self.token.getNome() == Tag.SIMB_FECHA_PARENTESES):
            self.sinalizaErroSintatico("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.ListaArg()

   # ListaArg’ → ","  ListaArg | ε
   def ListaArgLinha(self):
      if(self.eat(Tag.SIMB_VIRGULA)):
         self.sinalizaErroSintatico("Esperado\",\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         self.ListaArg
      
      elif(self.token.getNome() == Tag.SIMB_FECHA_PARENTESES):
         return

      else:
            self.skip("Esperado\", ou ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.ListaArgLinha()
   
   # Arg → TipoPrimitivo ID
   def Arg(self):
      if(self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or self.token.getNome() == Tag.KW_STRING or self.token.getNome() == Tag.KW_DOUBLE or self.token.getNome() == Tag.KW_VOID):
         self.TipoPrimitivo()

         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      # Synch: FOLLOW de Arg
      else:
         if(self.token.getNome() == Tag.SIMB_VIRGULA or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES):
            self.sinalizaErroSintatico("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Arg()
   
   # Retorno → "return" Expressao ";" | ε 
   def Retorno(self):
      if(self.eat(Tag.KW_RETURN)):
         
         self.Expressao()

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      elif(self.token.getNome() == Tag.KW_END):
         return
      
      else:
            self.skip("Esperado\"return ou ε\"; encontrado" + "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Retorno()

   # Main →"defstatic" "void" "main" "(" "String" "[" "]" ID ")" ":" RegexDeclaraId ListaCmd "end" ";"
   def Main(self):
      if(self.eat(Tag.KW_DEFSTATIC)):
         
         if(not self.eat(Tag.KW_VOID)):
            self.sinalizaErroSintatico("Esperado\"Void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.KW_MAIN)):
            self.sinalizaErroSintatico("Esperado\"main\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_ABRE_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.KW_STRING)):
            self.sinalizaErroSintatico("Esperado\"String\"; encontrado" + "\""+ self.token.getLexema() + "\"")

         if(not self.eat(Tag.SIMB_ABRE_COLCHETES)):
            self.sinalizaErroSintatico("Esperado\"[\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_FECHA_COLCHETES)):
            self.sinalizaErroSintatico("Esperado\"]\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_DOIS_PONTOS)):
            self.sinalizaErroSintatico("Esperado\":\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.RegexDeclaraId()
         self.ListaCmd()

         if(not self.eat(Tag.KW_END)):
            self.sinalizaErroSintatico("Esperado\"end\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      # Synch: FOLLOW de Main
      else:
         if(self.token.getNome() == Tag.KW_END):
            self.sinalizaErroSintatico("Esperado\"defstatic\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"defstatic\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Main()
   
   # TipoPrimitivo → "bool"| "integer" | "String" | "double" | "void"
   def TipoPrimitivo(self):
      noTipoPrimitivo = No()

      if(self.eat(Tag.KW_BOOL)):
         noTipoPrimitivo.setTipo(Tag.TIPOLOGICO)
         return noTipoPrimitivo

      elif(self.eat(Tag.KW_INTEGER)):
         noTipoPrimitivo.setTipo(Tag.TIPONUMERICO)
         return noTipoPrimitivo
      
      elif(self.eat(Tag.KW_STRING)):
         noTipoPrimitivo.setTipo(Tag.TIPOSTRING)
         return noTipoPrimitivo
      
      elif(self.eat(Tag.KW_DOUBLE)):
         noTipoPrimitivo.setTipo(Tag.TIPONUMERICO)
         return noTipoPrimitivo

      elif(self.eat(Tag.KW_VOID)):
         return noTipoPrimitivo
      
      # Synch: FOLLOW de TipoPrimitivo
      else:
         if(self.token.getNome() == Tag.ID):
            self.sinalizaErroSintatico("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.TipoPrimitivo()

   # ListaCmd → ListaCmd’ 
   def ListaCmd(self):
      if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN):
         self.ListaCmdLinha()

      # Synch: FOLLOW de ListaCmd
      else:
         if(self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"if, while, ID, write ou ε \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"if, while, ID, write ou ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.ListaCmd()

   # ListaCmd’ →  Cmd ListaCmd’ | ε 
   def ListaCmdLinha(self):
      if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE):
         self.Cmd()
         self.ListaCmdLinha()
      
      elif(self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
         return

      else:
            self.skip("Esperado\"if, while, ID, write ou ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.ListaCmdLinha()
   
   # Cmd → CmdIF | CmdWhile | ID CmdAtribFunc | CmdWrite
   def Cmd(self):
      if(self.token.getNome() == Tag.KW_IF):
         self.CmdIF()
      
      elif(self.token.getNome() == Tag.KW_WHILE):
         self.CmdWhile()
      
      elif(self.token.getNome() == Tag.ID):
         self.eat(Tag.ID)
         self.CmdAtribFunc()
      
      elif(self.token.getNome() == Tag.KW_WRITE):
         self.CmdWrite()

      # Synch: FOLLOW de Cmd
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"if, while, ID ou write\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"if, while, ID ou write\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Cmd()

   # CmdAtribFunc→ CmdAtribui | CmdFuncao
   def CmdAtribFunc(self):
      if(self.token.getNome() == Tag.OP_ATRIBUI):
         self.CmdAtribui()
      
      elif(self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.CmdFuncao()

      # Synch: FOLLOW de CmdAtribFunc
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\" = ou (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"= ou (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdAtribFunc()
   
   # CmdIF → "if" "(" Expressao ")" ":" ListaCmd CmdIF’
   def CmdIF(self):
      if(self.eat(Tag.KW_IF)):

         if(not self.eat(Tag.SIMB_ABRE_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_DOIS_PONTOS)):
            self.sinalizaErroSintatico("Esperado\":\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.ListaCmd()

         self.CmdIfLinha()
      
      # Synch: FOLLOW de CmdIF
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"if\"; encontrado" + "\""+ self.token.getLexema() + "\"")
            return 
         else:
            self.skip("Esperado\"if\"; encontrado" + "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdIF()

   # CmdIF’ → "end" ";" | "else" ":" ListaCmd "end" ";"
   def CmdIfLinha(self):
      if(self.eat(Tag.KW_END)):

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      elif(self.eat(Tag.KW_ELSE)):

         if(not self.eat(Tag.SIMB_DOIS_PONTOS)):
            self.sinalizaErroSintatico("Esperado\"(:)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.ListaCmd()

         if(not self.eat(Tag.KW_END)):
            self.sinalizaErroSintatico("Esperado\"end\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      # Synch: FOLLOW de CmdIfLinha
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"end ou else\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"end ou else\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdIfLinha()

   # CmdWhile → "while" "(" Expressao ")" ":" ListaCmd "end" ";"
   def CmdWhile(self):
      if(self.eat(Tag.KW_WHILE)):

         if(not self.eat(Tag.SIMB_ABRE_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         if(not self.eat(Tag.SIMB_DOIS_PONTOS)):
            self.sinalizaErroSintatico("Esperado\"(:)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.ListaCmd()

         if(not self.eat(Tag.KW_END)):
            self.sinalizaErroSintatico("Esperado\"end\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      # Synch: FOLLOW de CmdWhile
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"while\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"while\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdWhile()

   # CmdWrite → "write" "(" Expressao ")" ";"
   def CmdWrite(self):
      if(self.eat(Tag.KW_WRITE)):

         if(not self.eat(Tag.SIMB_ABRE_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      # Synch: FOLLOW de CmdWrite
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"wrile\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"wrile\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdWrite()

   # CmdAtribui → "=" Expressao ";"
   def CmdAtribui(self):
      if(self.eat(Tag.OP_ATRIBUI)):
         self.Expressao()

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      # Synch: FOLLOW de CmdAtribui
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"=\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"=\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdAtribui()
      
   # CmdFuncao → "(" RegexExp ")" ";"
   def CmdFuncao(self):
      if(self.eat(Tag.SIMB_ABRE_PARENTESES)):
         self.RegexExp()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      # Synch: FOLLOW de CmdFuncao
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.CmdFuncao()

   # RegexExp → Expressao RegexExp’ | ε 
   def RegexExp(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.SIMB_EXCLAMACAO or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.Expressao()

         self.RegexExpLinha()
      
      elif(self.token.getNome() == Tag.SIMB_FECHA_PARENTESES):
         return
      
      else:
         self.skip("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  ( , ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.RegexExp()

   # RegexExp’ → , Expressao RegexExp’| ε
   def RegexExpLinha(self):
      if(self.eat(Tag.SIMB_VIRGULA)):
         self.Expressao()

         self.RegexExpLinha()
      
      elif(self.token.getNome() == Tag.SIMB_FECHA_PARENTESES):
         return

      else:
         self.skip("Esperado\", ou ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.RegexExp()
   
   # Expressao → Exp1 Exp’
   def Expressao(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.SIMB_EXCLAMACAO or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.Exp1()

         self.ExpLinha()
      
      # Synch: FOLLOW de Expressao
      else:
         if(self.token.getNome() == Tag.SIMB_ABRE_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
            self.sinalizaErroSintatico("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Expressao()

   # Exp’ → "or" Exp1 Exp’  | "and" Exp1 Exp’  | ε 
   def ExpLinha(self):
      if(self.eat(Tag.OP_OR)):

         self.Exp1()

         self.ExpLinha()
      
      elif(self.eat(Tag.OP_AND)):

         self.Exp1()

         self.ExpLinha()
      
      elif(self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return

      else:
         self.skip("Esperado\"or, and ou ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.RegexExp()

   # Exp1 → Exp2 Exp1’
   def Exp1(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.Exp2()

         self.Exp1Linha()

      # Synch: FOLLOW de Exp1
      else:
         if(self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
            self.sinalizaErroSintatico("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Exp1()
   
   # Exp1’ → "<" Exp2 Exp1’ | "<=" Exp2 Exp1’ | ">" Exp2 Exp1’ | ">=" Exp2 Exp1’ | "==" Exp2 Exp1’ | "!=" Exp2 Exp1’  | ε
   def Exp1Linha(self):
      if(self.eat(Tag.OP_MENOR)):
         self.Exp2()
         self.Exp1Linha()
      
      elif(self.eat(Tag.OP_MENOR_IGUAL)):
         self.Exp2()
         self.Exp1Linha()
      
      elif(self.eat(Tag.OP_MAIOR)):
         self.Exp2()
         self.Exp1Linha()
      
      elif(self.eat(Tag.OP_MAIOR_IGUAL)):
         self.Exp2()
         self.Exp1Linha()
      
      elif(self.eat(Tag.OP_IGUAL)):
         self.Exp2()
         self.Exp1Linha()

      elif(self.eat(Tag.OP_DIFERENTE)):
         self.Exp2()
         self.Exp1Linha()
      
      elif(self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return

      else:
        self.skip("Esperado\"<, <=, >, >=,  ==, !=, ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
        if(self.token.getNome() != Tag.EOF):
            self.Exp1Linha()

   # Exp2 → Exp3 Exp2’
   def Exp2(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.Exp3()

         self.Exp2Linha()
      
      # Synch: FOLLOW de Exp2
      else:
         if(self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
            self.sinalizaErroSintatico("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\" ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Exp2()

   # Exp2’ → "+" Exp3 Exp2’ | "-" Exp3 Exp2’ | ε 
   def Exp2Linha(self):
      if(self.eat(Tag.OP_SOMA)):
         self.Exp3()
         self.Exp2Linha()

      elif(self.eat(Tag.OP_SUBTRAI)):
         self.Exp3()
         self.Exp2Linha()

      elif(self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return

      else:
         self.skip("Esperado\"+, - e ε \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.Exp2Linha()
   
   #Exp3 → Exp4 Exp3’
   def Exp3(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.Exp4()

         self.Exp3Linha()
      
      # Synch: FOLLOW de Exp3
      else:
         if(self.token.getNome() == Tag.OP_SOMA or self.token.getNome() == Tag.OP_SUBTRAI or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
            self.sinalizaErroSintatico("Esperado\"  ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"  ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Exp3()
   
   # Exp3’ → "*" Exp4 Exp3’ | "/" Exp4 Exp3’ | ε
   def Exp3Linha(self):
      if(self.eat(Tag.OP_MULT)):
         self.Exp4()
         self.Exp3Linha()
      
      elif(self.eat(Tag.OP_DIV)):
         self.Exp4()
         self.Exp3Linha()

      elif(self.token.getNome() == Tag.OP_SOMA or self.token.getNome() == Tag.OP_SUBTRAI or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return
      
      # Synch: FOLLOW de Exp3Linha
      else:
         self.skip("Esperado\" *, / e ε \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.Exp3Linha()
   
   # Exp4 → ID Exp4’ | CONST_INT | CONST_DOUBLE | CONST_STRING  | "true" | "false" | OpUnario Exp4 | "(" Expressao")"  
   def Exp4(self):
      if(self.eat(Tag.ID)):
         self.Exp4Linha()

      elif(self.eat(Tag.CONST_INT)):
         return
      elif(self.eat(Tag.CONST_DOUBLE)):
         return      
      elif(self.eat(Tag.CONST_STRING)):
         return
      elif(self.eat(Tag.KW_TRUE)):
         return
      elif(self.eat(Tag.KW_FALSE)):
         return
      elif(self.token.getNome() == Tag.OP_UNARIO):
         self.OpUnario()
         self.Exp4()
      
      elif(self.eat(Tag.SIMB_ABRE_PARENTESES)):

         self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\" ) \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

      
      # Synch: FOLLOW de Exp4
      else:
         if(self.token.getNome() == Tag.OP_MULT or self.token.getNome() == Tag.OP_DIV or self.token.getNome() == Tag.OP_SOMA or self.token.getNome() == Tag.OP_SUBTRAI or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
            self.sinalizaErroSintatico("Esperado\"  ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"  ID,  CONST_INT, CONST_DOUBLE, CONST_STRING, true,  false, -(negação) , !,  (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.Exp4()
   
   # Exp4’ → "(" RegexExp ")" | ε
   def Exp4Linha(self):
      if(self.eat(Tag.SIMB_ABRE_PARENTESES)):
         self.RegexExp()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      elif(self.token.getNome() == Tag.OP_MULT or self.token.getNome() == Tag.OP_DIV or self.token.getNome() == Tag.OP_SOMA or self.token.getNome() == Tag.OP_SUBTRAI or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return

      else:
         self.skip("Esperado\" ( ou ε \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.Exp4Linha()
   
   # OpUnario → "-" | "!"
   def OpUnario(self):
      if(self.eat(Tag.OP_SUBTRAI)):
         return
      
      elif(self.eat(Tag.SIMB_EXCLAMACAO)):
         return
      
      # Synch: FOLLOW de OpUnario
      else:
         if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.SIMB_EXCLAMACAO or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
            self.sinalizaErroSintatico("Esperado\" -(negação) e !\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return
         else:
            self.skip("Esperado\"-(negação) e ! \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               self.OpUnario()