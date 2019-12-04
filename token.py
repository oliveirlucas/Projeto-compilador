import Tag from tag
class Token:
   '''
   Classe que representa um token
   '''
   def __init__(self, nome, lexema, linha, coluna):
      self.nome = nome
      self.lexema = lexema
      self.linha = linha
      self.coluna = coluna
      self.tipo = Tag.TIPOVAZIO

   def getNome(self):
      return self.nome

   def getLexema(self):
      return self.lexema
   
   def setTipo(self,tipo):
      self.tipo = tipo

   def getLinha(self):
      return self.linha

   def setLinha(self, linha):
      self.linha = linha

   def getColuna(self):
      return self.coluna

   def setColuna(self, coluna):
      self.coluna = coluna

   def toString(self):
      return "<" + str(self.nome.name) + ", \"" + str(self.lexema) + "\">"
