# encoding: utf-8

import gvsig

from org.gvsig.fmap.geom.aggregate import MultiPolygon
from org.gvsig.fmap.geom import GeometryUtils
from org.gvsig.scripting.app.extension import ScriptingUtils

import xmltodic


def null2empty(n):
  if n==None:
    return ""
  return n

def null2zero(n):
  if n==None:
    return 0
  return n

class SIGPACDeclaracionParser(object):
  
  def __init__(self, fname):
    self.fname = fname
    self.xml = None
    self.lineaCorriente = None
    self.lineas = None
    self._ID_DECLARACION = ""
    self._NOMBRE = ""
    self._CIF_NIF = ""
    self.srs = None
    
  def open(self):
    fileXml = open(self.fname,"r")
    data = fileXml.read()
    fileXml.close()
    self.xml = xmltodic.parse(data)
    
    srid = self.getSRId()
    if srid != None:
      self.srs = "EPSG:"+srid
    
    declarante = self.xml["DECLARACION"].get("DECLARANTE",None)
    if declarante != None:
      self._ID_DECLARACION = null2empty(declarante.get("ID_DECLARACION",None))
      self._NOMBRE = null2empty(declarante.get("NOMBRE",None))
      self._CIF_NIF = null2empty(declarante.get("CIF_NIF",None))
    
    self.lineas = self.getLineas()

    self.rewind()

  def getSRId(self):
    try:
      return self.xml["DECLARACION"]["METADATA"]["SRID"]
    except:
      return None
  
  def rewind(self):
    self.lineaCorriente = 0
  
  def getLineas(self):
    lineas = self.xml["DECLARACION"]["LINEA_DECLARACION"]
    if not isinstance(lineas,list):
      lineas = [ lineas ]
    return lineas
  
  def read(self):
    lineas = self.getLineas()
    if self.lineaCorriente >= len(lineas):
      return None
    linea = lineas[self.lineaCorriente]
    ID_ALE = null2zero(linea.get("ID_ALE", None))
    wkt = linea.get("WKT",None)
    if "EMPTY" in wkt:
      ScriptingUtils.log(ScriptingUtils.WARN, "La geometria no es valida (ID_ALE=%s), el poligono esta vacio" % (ID_ALE))
      geom = None
    elif wkt != None:
      geom = GeometryUtils.createFrom(wkt, self.srs)
      if not geom.isValid():
        #status = geom.getValidationStatus()
        msg = ""#status.getMessage()
        ScriptingUtils.log(ScriptingUtils.WARN, "La geometria no es valida (ID_ALE=%s), %s" % (ID_ALE, msg))
        geom = None
        
    if geom!=None and not isinstance(geom,MultiPolygon):
      geom = geom.toPolygons()

    values = [
      self._ID_DECLARACION,
      self._NOMBRE,
      self._CIF_NIF,
      ID_ALE,
      null2zero(linea.get("ID_EXP", None)),
      null2empty(linea.get("EXP_COD", None)),
      null2empty(linea.get("TEX_NIF", None)),
      null2zero(linea.get("ID_CROQUIS", None)),
      null2zero(linea.get("PROV", None)),
      null2zero(linea.get("MUN_CAT", None)),
      null2zero(linea.get("AGREGADO", None)),
      null2zero(linea.get("ZONA", None)),
      null2zero(linea.get("POLIGONO", None)),
      null2zero(linea.get("PARCELA", None)),
      null2zero(linea.get("RECINTO", None)),
      null2empty(linea.get("COD_TIPO_ALE", None)),
      null2empty(linea.get("USO", None)),
      null2zero(linea.get("SUPERFICIE_DECLARADA", None)),
      null2zero(linea.get("COEF_REG", None)),
      null2zero(linea.get("SECANO_REGADIO", None)),
      null2zero(linea.get("ELEGIBILIDAD", None)),
      null2zero(linea.get("FC_ALMENDROS", None)),
      null2zero(linea.get("FC_ALGARROBOS", None)),
      null2zero(linea.get("FC_AVELLANOS", None)),
      null2zero(linea.get("FC_NOGALES", None)),
      null2zero(linea.get("FC_PISTACHOS", None)),
      null2zero(linea.get("FC_TOTAL", None)),
      null2zero(linea.get("DN_SURFACE", None)),
      geom
    ]
    self.next()
    return values

  def next(self):
    self.lineaCorriente += 1

