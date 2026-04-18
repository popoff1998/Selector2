# -*- coding: utf-8 -*-
"""
Created on Thu Mar 07 08:35:11 2013

@author: tonin

Parser-sesiones para selector-ng

"""
import inspect
import re
from collections import defaultdict
from pprint import pprint
from qt_compat import QtCore, QtGui
from selector_ng import Pixmap , SESSIONS_LIMIT
import copy


class session(object):
    """Objeto para almacenar una sesion"""
    def __init__(self,indice,valores,sep_x,teclasSelector,parent):
        self.indice = indice
        self.valores = valores
        self.title = valores["TITLE"]
        self.type = valores["TYPE"]
        self.vt = int(valores["SCREEN"]) + 3

        # Permite tipos con o sin extension y mantiene compatibilidad.
        icon_name = self.type.strip()
        if "." in icon_name:
            candidate_paths = [":/" + icon_name]
        else:
            candidate_paths = [
                ":/" + icon_name + ".png",
                ":/" + icon_name + ".jpg",
                ":/" + icon_name + ".jpeg",
            ]

        pixmap_rc = candidate_paths[0]
        for path in candidate_paths:
            pix = QtGui.QPixmap(path)
            if not pix.isNull():
                pixmap_rc = path
                break
        self.numeroSesiones = parent.numeroSesiones
        self.pixmap = Pixmap(QtGui.QPixmap(pixmap_rc),self,sep_x,teclasSelector) 
        
class config(object):
    """Objeto que almacena un fichero de configuracion
       Atributos:
           text: El texto del fichero
           
       """
    def __init__(self,filename):
        try:
            f = open(filename,"r")
        except Exception:
            print("El fichero ", filename, " no existe")
            return False
        self.text = f.readlines()
        self.sessionsDict={}
        self.sessionsList=[]
        self.numeroSesiones = 0
        self.getSessionsList()
        
    def getSessionsRawList(self):
        """Parsea de text las lineas creando objetos session
        con las lineas de configuracion en modo raw devolviendo una list"""
        
        #Elimina las lineas de comentario o en blanco
        text = [x for x in self.text if re.search('^[^#].', x)]
        #Parsea los elementos de SESSION
        raw = [re.findall("SESSION_([0-9])_(.*)=(.*)", x) for x in text]
        #Eliminamos los elementos vacios
        self.sessionsRawList = [x for x in raw if len(x) > 0]
        self.sessionsRawList.sort()
        return self.sessionsRawList
    
    def getSessionsDict(self):
        """"
        Devuelve un diccionario a partir de la lista raw de sesiones.
        
        Está deprecated ya que es mucho más dificil manejarse con un 
        diccionario de diccionarios que con una lista de diccionarios
        al tener variables ligadas al índice como es la tecla a mostrar
        """
        for linea in self.getSessionsRawList():
            for indice,var,value in linea:
                if int(indice) < SESSIONS_LIMIT or SESSIONS_LIMIT == 0:
                    self.sessionsDict.setdefault(indice,{})[var] = value   
        return self.sessionsDict

    def getSessionsList(self):
        l = self.getSessionsRawList()
        for linea in l:
            for indice,var,value in linea:
                index = int(indice)
                if len(self.sessionsList) < index+1:
                    self.sessionsList.append({})
                self.sessionsList[int(indice)].setdefault(var,value)
        #Borro la sesion del selector
        self.sessionsList = [x for x in self.sessionsList
                     if x.get('TYPE') != 'selector']
        #Borro las sesiones mayores que sessions limit
        self.sessionsList = [x for x in self.sessionsList
                     if self.sessionsList.index(x) < SESSIONS_LIMIT or
                     SESSIONS_LIMIT == 0]
        self.numeroSesiones = len(self.sessionsList)
        return self.sessionsList

    def rellenaSesiones(self,sep_x,teclasSelector):
        self.sesiones = []        
        for i in self.sessionsList:
            sess = session(self.sessionsList.index(i),i,sep_x,teclasSelector,self)
            self.sesiones.append(sess)
                
    
        
        
        
"""
# Codigo de pruebas            

p = config("/etc/thinstation.network")

#print p.text
lista = p.getSessionsRawList()
l = p.getSessionsList()
pprint(l)
print "Numero sesiones = ",p.numeroSesiones

p.rellenaSesiones(10)


#dictionary = p.getSessionsDict()
print lista
print "\n\n"
print dictionary
print "\n\n"
print dictionary.keys()
print "\n\n"
pprint(dictionary)  
print len(dictionary)
for kk in dictionary: print kk,len(dictionary.get(kk))
print p.numeroSesiones

p.rellenaSesiones()


for i in p.sesiones:
    print "\nSESION NUMERO ", i.indice
    for property, value in vars(i).iteritems():
        print property, ": ", value

"""