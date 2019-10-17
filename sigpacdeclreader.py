# encoding: utf-8

import gvsig

from gvsig import getResource

import re
import os.path

from java.net import URL
from java.io import File

from org.gvsig.fmap.dal.feature.spi.simpleprovider import AbstractSimpleSequentialReaderFactory
from org.gvsig.fmap.dal.feature.spi.simpleprovider import SimpleSequentialReader

from sigpacdeclparser import SIGPACDeclaracionParser



class SIGPACDeclaracionReaderFactory(AbstractSimpleSequentialReaderFactory):

  def __init__(self):
    AbstractSimpleSequentialReaderFactory.__init__(self, "SIGPACDECL", "SIGPAC fichero de declaraciones", ("xml",))

  def accept(self, pathname):
    # Este metodo es opcional, si con la extension del fichero es
    # suficiente, no hace falta sobreescribirlo.
    if not AbstractSimpleSequentialReaderFactory.accept(self,pathname):
      return False
    f = open(pathname.getAbsolutePath(),"r")
    head = f.read(500)
    f.close()
    head = head.lower()
    head = head.replace("\r","").replace("\n"," ")
    #print pathname, repr(head)
    return ("<declaracion>" in head) and ("<declarante" in head) and ("<linea_declaracion>" in head)

  def fetchDefaultParameters(self, params):
    # Este metodo es opcional, si el fichero de datos no aporta ningun valor
    # de entre los requeridos en los parametros (como es el SRS), no hace
    # falta sobreescribirlo.
    srid = None
    if params.getFile().length()<10000:
      # Si el fichero es pequeño se parsea el XML para obtener el SRS
      parser = SIGPACDeclaracionParser(params.getFile().getAbsolutePath())
      parser.open()
      srid = parser.getSRId()
    else:
      # Si el fichero es grande miramos a ver si en las primeras linas
      # encontramos el SRS.
      pathname = params.getFile().getAbsolutePath()
      f = open(pathname,"r")
      head = f.read(500)
      f.close()
      head = head.lower()
      head = head.replace("\r","").replace("\n"," ")
      m = re.compile(".*<srid>([0-9]*)</srid>.*").match(head)
      if m!=None:
        srid = m.group(1)
    if srid!=None:
      params.setDynValue("CRS","EPSG:%s" % srid)
    

  def createReader(self, params):
    reader = SIGPACDeclaracionReader(self, params)
    return reader
  
class SIGPACDeclaracionReader(SimpleSequentialReader):

  def __init__(self, factory, parameters):
    self._factory = factory
    self._parameters = parameters
    self._parser = None

  def getFactory(self):
    return self._factory

  def getName(self):
    return os.path.splitext(self._parameters.getFile().getName())[0]
    
  def getFieldNames(self):
    fields = [
      "ID_DECLARACION:String:size:100",
      "NOMBRE:String:size:100",
      "CIFNIF:String:size:20",
      "ID_ALE:INTEGER",
      "ID_EXP:INTEGER",
      "EXP_COD:STRING:size:25",
      "TEX_NIF:STRING:size:25",
      "ID_CROQUIS:INTEGER",
      "PROV:INTEGER",
      "MUN_CAT:INTEGER",
      "AGREGADO:INTEGER",
      "ZONA:INTEGER",
      "POLIGONO:INTEGER",
      "PARCELA:INTEGER",
      "RECINTO:INTEGER",
      "COD_TIP_AL:STRING:size:25",
      "USO:STRING:size:100",
      "SUPERF_DEC:DOUBLE",
      "COEF_REG:DOUBLE",
      "SECANO_REG:DOUBLE",
      "ELEGIBILID:DOUBLE",
      "FC_ALMENDR:DOUBLE",
      "FC_ALGARRO:DOUBLE",
      "FC_AVELLAN:DOUBLE",
      "FC_NOGALES:DOUBLE",
      "FC_PISTACH:DOUBLE",
      "DN_SURFACE:DOUBLE",
      "FC_TOTAL:DOUBLE",
      "GEOMETRY:MultiPolygon:geomSubtype:2D"
    ]
    return fields
  
    
  def getFile(self):
    return self._parameters.getFile()
    
  def read(self):
    if self._parser == None:
      self._parser = SIGPACDeclaracionParser(self._parameters.getFile().getAbsolutePath())
      self._parser.open()
    return self._parser.read()
    
  def rewind(self):
    if self._parser == None:
      self._parser = SIGPACDeclaracionParser(self._parameters.getFile().getAbsolutePath())
      self._parser.open()
    self._parser.rewind()
    
  def close(self):
    self._parser = None


def selfRegister():
  factory = SIGPACDeclaracionReaderFactory()
  factory.selfRegister(
    URL("file://"+getResource(__file__,"SIGPACDeclParameters.xml")),
    URL("file://"+getResource(__file__,"SIGPACDeclMetadata.xml")),
  )

def test(factory, fname):
  if not factory.accept(File(fname)):
    print "File not supported by this factory ", factory.getName()
    return
  params = factory.createStoreProviderFactory().createParameters()
  params.setFile(File(fname))
  factory.fetchDefaultParameters(params)
  reader = factory.createReader(params)
  print "Reader: ", reader.getFactory().getName()
  print "Name: ", reader.getName()
  print "File: ", reader.getFile()
  print "Fields: ", reader.getFieldNames()

  n = 0
  line = reader.read()
  while line!=None and n<10:
    print line
    line = reader.read()
    n += 1
  reader.close()
  reader.rewind() # test rewind
    

def main(*args):
  selfRegister()
  #test(SIGPACDeclaracionReaderFactory(), "/home/jjdelcerro/datos/geodata/vector/sigpac/2018/Declaracion3.xml")
  test(SIGPACDeclaracionReaderFactory(), "/home/jjdelcerro/datos/geodata/vector/sigpac/2018/ALS_20180413142453-CroquisAlegado.xml")
  