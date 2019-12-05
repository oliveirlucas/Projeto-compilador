import sys
import copy

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

         tempToken = copy.copy(self.token)
         
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" + "\""+ self.token.getLexema() + "\"")
         else:
            self.lexer.ts.setTipo(tempToken.getLexema(), Tag.TIPOVAZIO)
         
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

         noTipoPrimitivo = self.TipoPrimitivo()

         tempToken = copy.copy(self.token)

         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         else:
            self.lexer.ts.setTipo(tempToken.getLexema(), noTipoPrimitivo.getTipo())
         
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
         if(noRetorno.getTipo() != noTipoPrimitivo.getTipo()):
            self.sinalizaErroSemantico("Tipo de retorno incompativel")


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
         noTipoPrimitivo = self.TipoPrimitivo()

         tempToken = copy.copy(self.token)

         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         else:
            self.lexer.ts.setTipo(tempToken.getLexema(), noTipoPrimitivo.getTipo())

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

      noRetorno = No()
      if(self.eat(Tag.KW_RETURN)):
         
         noExpressao = self.Expressao()

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         noRetorno.setTipo(noExpressao.getTipo())
      
      elif(self.token.getNome() == Tag.KW_END):
         noRetorno.setTipo(Tag.TIPOVAZIO)
         return
      
      else:
         self.skip("Esperado\"return ou ε\"; encontrado" + "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            return self.Retorno()
      return noRetorno

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

         tempToken = copy.copy(self.token)
         
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado\"ID\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         else:
            self.lexer.ts.setTipo(tempToken.getLexema(), Tag.TIPOSTRING)
         
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
            return noTipoPrimitivo
         else:
            self.skip("Esperado\"bool, interger, String, double, void\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               return self.TipoPrimitivo()
      return noTipoPrimitivo

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
      tempToken = copy.copy(self.token)
      if(self.token.getNome() == Tag.KW_IF):
         self.CmdIF()
      
      elif(self.token.getNome() == Tag.KW_WHILE):
         self.CmdWhile()

      elif(self.token.getNome() == Tag.ID):
         self.eat(Tag.ID)

         if(self.lexer.ts.getTipo(tempToken.getLexema()) is None ):
            self.sinalizaErroSemantico("ID não declarado")

         noCmdAtribFunc = self.CmdAtribFunc()

         if(noCmdAtribFunc.getTipo() != Tag.TIPOVAZIO and self.lexer.ts.getTipo(tempToken.getLexema()) != noCmdAtribFunc.getTipo()):
            self.sinalizaErroSemantico("Atribuição incompatível")

      
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
      noCmdAtribFunc = No()

      if(self.token.getNome() == Tag.OP_ATRIBUI):
         noCmdAtribui = self.CmdAtribui()
      
         noCmdAtribFunc.setTipo(noCmdAtribui.getTipo())
      
      elif(self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         self.CmdFuncao()
      
         noCmdAtribFunc.setTipo(Tag.TIPOVAZIO) 

      # Synch: FOLLOW de CmdAtribFunc
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\" = ou (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return noCmdAtribFunc
         else:
            self.skip("Esperado\"= ou (\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               return self.CmdAtribFunc()
      return noCmdAtribFunc

   # CmdIF → "if" "(" Expressao ")" ":" ListaCmd CmdIF’
   def CmdIF(self):
      if(self.eat(Tag.KW_IF)):

         if(not self.eat(Tag.SIMB_ABRE_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\"(\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         noExpressao = self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            
         if(noExpressao.getTipo() != Tag.TIPOLOGICO):
            self.sinalizaErroSemantico("Erro Logico")
         
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
         
         noExpressao = self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(noExpressao.getTipo() != Tag.TIPOLOGICO):
            self.sinalizaErroSemantico("Erro Logico")

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
         
         noExpressao = self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\")\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         
         if(noExpressao.getTipo() != Tag.TIPOSTRING):
            self.sinalizaErroSemantico("Erro String")
         
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
      noCmdAtribui = No()

      if(self.eat(Tag.OP_ATRIBUI)):
         noExpressao = self.Expressao()

         noCmdAtribui.setTipo(noExpressao.getTipo())

         if(not self.eat(Tag.SIMB_PONTO_VIRGULA)):
            self.sinalizaErroSintatico("Esperado\"(;)\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
      
      # Synch: FOLLOW de CmdAtribui
      else:
         if(self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE):
            self.sinalizaErroSintatico("Esperado\"=\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            return noCmdAtribui
         else:
            self.skip("Esperado\"=\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
            if(self.token.getNome() != Tag.EOF):
               return self.CmdAtribui()
      return noCmdAtribui

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
         noExp1 = self.Exp1()

         noExpLinha = self.ExpLinha()

         if(noExpLinha.getTipo() == Tag.TIPOVAZIO):
            noExp1.setTipo(noExpLinha.getTipo())
         elif(noExpLinha.getTipo() == noExp1.getTipo() and noExpLinha.getTipo() == Tag.TIPOLOGICO):
            noExpLinha.setTipo(Tag.TIPOLOGICO)
         else:
            noExpLinha.setTipo(Tag.TIPOERRO)
      
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

         noExp1 = self.Exp1()

         noExpLinha = self.ExpLinha()

         if(noExpLinha.getTipo() == Tag.TIPOVAZIO and noExp1.getTipo() == Tag.TIPOLOGICO):
            noExpLinha.setTipo(Tag.TIPOLOGICO)
         elif(noExpLinha.getTipo() == noExp1.getTipo() and noExp1.getTipo() == Tag.TIPOLOGICO):
            noExpLinha.setTipo(Tag.TIPOLOGICO)
         else:
            noExpLinha.setTipo(Tag.TIPOERRO)
      
      elif(self.eat(Tag.OP_AND)):

         noExp1 = self.Exp1()

         noExpLinha = self.ExpLinha()

         if(noExpLinha.getTipo() == Tag.TIPOVAZIO and noExp1.getTipo() == Tag.TIPOLOGICO):
            noExpLinha.setTipo(Tag.TIPOLOGICO)
         elif(noExpLinha.getTipo() == noExp1.getTipo() and noExp1.getTipo() == Tag.TIPOLOGICO):
            noExpLinha.setTipo(Tag.TIPOLOGICO)
         else:
            noExpLinha.setTipo(Tag.TIPOERRO)
      
      elif(self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         noExpLinha.setTipo(Tag.TIPOVAZIO)
         return

      else:
         self.skip("Esperado\"or, and ou ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.RegexExp()

   # Exp1 → Exp2 Exp1’
   def Exp1(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         noExp2 = self.Exp2()

         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO):
            noExp1Linha.setTipo(noExp2.getTipo())
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp1Linha.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPOLOGICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)

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
         noExp2 = self.Exp2()
         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)
      
      elif(self.eat(Tag.OP_MENOR_IGUAL)):
         noExp2 = self.Exp2()
         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)
      
      elif(self.eat(Tag.OP_MAIOR)):
         noExp2 = self.Exp2()
         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)
      
      elif(self.eat(Tag.OP_MAIOR_IGUAL)):
         noExp2 = self.Exp2()
         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)
      
      elif(self.eat(Tag.OP_IGUAL)):
         noExp2 = self.Exp2()
         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)
      elif(self.eat(Tag.OP_DIFERENTE)):
         noExp2 = self.Exp2()
         noExp1Linha = self.Exp1Linha()

         if(noExp1Linha.getTipo() == Tag.TIPOVAZIO and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         elif(noExp1Linha.getTipo() == noExp2.getTipo() and noExp2.getTipo() == Tag.TIPONUMERICO):
            noExp1Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp1Linha.setTipo(Tag.TIPOERRO)
      
      elif(self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return

      else:
        self.skip("Esperado\"<, <=, >, >=,  ==, !=, ε\"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
        if(self.token.getNome() != Tag.EOF):
            self.Exp1Linha()

   # Exp2 → Exp3 Exp2’
   def Exp2(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         noExp3 = self.Exp3()

         noExp2Linha = self.Exp2Linha()

         if(noExp2Linha.getTipo() == Tag.TIPOVAZIO):
            noExp2Linha.setTipo(noExp3.getTipo())
         elif(noExp2Linha.getTipo() == noExp3.getTipo() and noExp2Linha.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp2Linha.setTipo(Tag.TIPOERRO)

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
         noExp3 = self.Exp3()
         noExp2Linha = self.Exp2Linha()

         if(noExp2Linha.getTipo() == Tag.TIPOVAZIO and noExp3.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(tag.TIPONUMERICO)
         elif(noExp2Linha.getTipo() == noExp3.getTipo() and noExp3.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp2Linha.setTipo(Tag.TIPOERRO)

      elif(self.eat(Tag.OP_SUBTRAI)):
         noExp3 = self.Exp3()
         noExp2Linha = self.Exp2Linha()

         if(noExp2Linha.getTipo() == Tag.TIPOVAZIO and noExp3.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(tag.TIPONUMERICO)
         elif(noExp2Linha.getTipo() == noExp3.getTipo() and noExp3.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp2Linha.setTipo(Tag.TIPOERRO)

      elif(self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         return

      else:
         self.skip("Esperado\"+, - e ε \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.Exp2Linha()
   
   #Exp3 → Exp4 Exp3’
   def Exp3(self):
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.CONST_INT or self.token.getNome() == Tag.CONST_DOUBLE or self.token.getNome() == Tag.CONST_STRING or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.SIMB_ABRE_PARENTESES):
         noExp4 = self.Exp4()

         noExp3Linha = self.Exp3Linha()

         if(noExp3Linha.getTipo() == Tag.TIPOVAZIO):
            noExp4.setTipo()
         elif(noExp3Linha.getTipo() == noExp4.getTipo() and noExp3Linha.getTipo() == Tag.TIPONUMERICO):
            noExp3Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp3Linha.setTipo(Tag.TIPOERRO)
      
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
         noExp4 = self.Exp4()
         noExp3Linha = self.Exp3Linha()
      
         if(noExp3Linha.getTipo() == Tag.TIPOVAZIO and noExp4.getTipo() == Tag.TIPONUMERICO):
            noExp3Linha.setTipo(tag.TIPONUMERICO)
         elif(noExp3Linha.getTipo() == noExp4.getTipo() and noExp4.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp2Linha.setTipo(Tag.TIPOERRO)

      elif(self.eat(Tag.OP_DIV)):

         noExp4 = self.Exp4()
         noExp3Linha = self.Exp3Linha()
      
         if(noExp3Linha.getTipo() == Tag.TIPOVAZIO and noExp4.getTipo() == Tag.TIPONUMERICO):
            noExp3Linha.setTipo(tag.TIPONUMERICO)
         elif(noExp3Linha.getTipo() == noExp4.getTipo() and noExp4.getTipo() == Tag.TIPONUMERICO):
            noExp2Linha.setTipo(Tag.TIPONUMERICO)
         else:
            noExp2Linha.setTipo(Tag.TIPOERRO)

      elif(self.token.getNome() == Tag.OP_SOMA or self.token.getNome() == Tag.OP_SUBTRAI or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_OR or self.token.getNome() == Tag.OP_AND or self.token.getNome() == Tag.SIMB_FECHA_PARENTESES or self.token.getNome() == Tag.SIMB_PONTO_VIRGULA or self.token.getNome() == Tag.SIMB_VIRGULA):
         noExp3Linha.setTipo(Tag.TIPOVAZIO)
         return
      
      # Synch: FOLLOW de Exp3Linha
      else:
         self.skip("Esperado\" *, / e ε \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")
         if(self.token.getNome() != Tag.EOF):
            self.Exp3Linha()
   
   # Exp4 → ID Exp4’ | CONST_INT | CONST_DOUBLE | CONST_STRING  | "true" | "false" | OpUnario Exp4 | "(" Expressao")"  
   def Exp4(self):

      tempToken = copy.copy(self.token)
            
      if(self.eat(Tag.ID)):
         noExp4Linha = self.Exp4Linha()
         self.lexer.ts.getTipo(tempToken.getLexema())

         if(noExp4Linha is None):
            noExp4Linha.setTipo(Tag.TIPOERRO)
            self.sinalizaErroSemantico("ID não declarado")

      elif(self.eat(Tag.CONST_INT)):
         noExp4Linha.setTipo(Tag.TIPONUMERICO)
         return
      elif(self.eat(Tag.CONST_DOUBLE)):
         noExp4Linha.setTipo(Tag.TIPONUMERICO)
         return      
      elif(self.eat(Tag.CONST_STRING)):
         noExp4Linha.setTipo(Tag.TIPOSTRING)
         return
      elif(self.eat(Tag.KW_TRUE)):
         noExp4Linha.setTipo(Tag.TIPOLOGICO)
         return
      elif(self.eat(Tag.KW_FALSE)):
         noExp4Linha.setTipo(Tag.TIPOLOGICO)
         return
      elif(self.token.getNome() == Tag.OP_UNARIO):
         noOpUnario = self.OpUnario()
         noExp4 = self.Exp4()

         if(noExp4.getTipo() == noOpUnario.getTipo() and noOpUnario.getTipo() == Tag.TIPONUMERICO):
            noExp4.setTipo(tag.TIPONUMERICO)
         elif(noExp4.getTipo() == noOpUnario.getTipo() and noOpUnario.getTipo() == Tag.TIPOLOGICO):
            noExp4.setTipo(Tag.TIPOLOGICO)
         else:
            noExp4.setTipo(Tag.TIPOERRO)
      
      elif(self.eat(Tag.SIMB_ABRE_PARENTESES)):

         noExpressao = self.Expressao()

         if(not self.eat(Tag.SIMB_FECHA_PARENTESES)):
            self.sinalizaErroSintatico("Esperado\" ) \"; encontrado" "+" "\""+ self.token.getLexema() + "\"")

         noExp4.setTipo(noExpressao.getTipo())
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
         OpUnario.setTipo(Tag.TIPONUMERICO)
         return
      
      elif(self.eat(Tag.SIMB_EXCLAMACAO)):
         OpUnario.setTipo(Tag.TIPOLOGICO)
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