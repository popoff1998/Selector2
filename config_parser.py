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
from PyQt4 import QtCore, QtGui
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
        pixmap_rc = ":/"+self.type+".png"
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
        except:
            print "El fichero ",filename," no existe"
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
        text = filter( lambda x:re.search('^[^#].',x), self.text)
        #Parsea los elementos de SESSION
        raw = map( lambda x:re.findall( "SESSION_([0-9])_(.*)=(.*)",x), text)
        #Eliminamos los elementos vacios
        self.sessionsRawList = filter(lambda x:len(x)>0, raw)
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
        pprint(l)
        for linea in l:
            print linea
            for indice,var,value in linea:
                index = int(indice)
                if len(self.sessionsList) < index+1:
                    self.sessionsList.append({})
                self.sessionsList[int(indice)].setdefault(var,value)
        #Borro la sesion del selector
        self.sessionsList = filter(lambda x:x.get('TYPE') != 'selector',
                                  self.sessionsList)             
        #Borro las sesiones mayores que sessions limit
        self.sessionsList = filter(lambda x:self.sessionsList.index(x) < SESSIONS_LIMIT or\
                                            SESSIONS_LIMIT == 0, self.sessionsList)
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