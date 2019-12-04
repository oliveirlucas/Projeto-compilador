from tag import Tag

class No():
   def __init__(self):
      self.tipo = Tag.TIPOVAZIO

   def getTipo(self):
      return self.tipo
   
   def setTipo(self,tipo):
      self.tipo = tipo