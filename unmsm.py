import requests.api
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import os, errno, time

class Unmsm:

    def __init__(self, concurso):
        self.concurso = concurso
        self.__sedes = {}
        self.__url = f"http://unmsm.claro.net.pe/{concurso}"

        self.__eapPorSede()


    def htmlContent(self, url):
        """Retorna la instancia de BeautifulSoup"""
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
            return None
        else:
            return BeautifulSoup(response.content, "lxml")

    def getSedes(self):
        """Obtiene todas las sedes disponibles"""
        return [sede for sede in self.__sedes.keys()]

    def getEAPs(self, sede):
        """Obtiene todos los EAPs disponibles de acuerdo a la Sede"""
        return [eap for eap in self.__sedes[sede.upper()]]

    def importarEap(self, sede, eap, path=None):
        """Importa el csv correspondiente a la Sede y EAP"""
        cod_sede_eap = self.__sedes[sede.upper()][eap.upper()]
        index_escuela = self.htmlContent(f'{self.__url}/{cod_sede_eap}/0.html')
        headers = [tag.b.unwrap().text if tag.b is not None else tag.text for tag in index_escuela.thead.tr.children]
        if index_escuela.tfoot is None:
            pags = ['0.html']
        else:
            td_children = index_escuela.tfoot.tr.td.children
            pags = [a['href'] for a in td_children ]

        if path is None:
            self.__crearCSV(self.__listarPostulantes(cod_sede_eap, pags), headers, sede, eap)
        else:
            self.__crearCSV(self.__listarPostulantes(cod_sede_eap, pags), headers, sede, eap, path)


    def importarTodo(self, path=None):
        """Importa todos los datos de la página organizados por Sede"""
        if path is None:
            path = self.concurso
        else:
            path = os.path.join(path, self.concurso)

        try:
            os.mkdir(path)
            for sede in self.getSedes():
                os.makedirs(f'{path}/{sede}', exist_ok=True)
                for eap in self.getEAPs(sede):
                    subdir_sede = os.path.join(path, sede)
                    self.importarEap(sede, eap, subdir_sede)
                    # time.sleep(1) produce 1s de retraso (para no sobrecargar de peticiones a la pag)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise

    def __eapPorSede(self):
        """Guarda las EAPs por cada Sede"""
        index = self.htmlContent(f'{self.__url}/index.html') 

        for sede in index.find_all('a'):
            escuelas = self.htmlContent(f"{self.__url}/{sede['href']}") #EAPs de cada sede   
            eap = {}

            for eaps in escuelas.find_all('a'):
                if eaps['href'] not in 'index.html':
                    eap[eaps.text] = '/'.join(eaps['href'].split('/')[1:3])

            self.__sedes[sede.text] = eap


    def __crearCSV(self, postulantes, columnas, sede, eap, path=None):
        """Crea el archivo csv"""
        df = pd.DataFrame(postulantes, columns=columnas)
        if path is None:
            df.to_csv(f'{self.concurso}-{sede}-{eap}.csv', index=False)
        else:
            df.to_csv(os.path.join(path, f'{self.concurso}-{sede}-{eap}.csv'), index=False)


    def __listarPostulantes(self, cod_sede_eap, pags):
        """Retorna una lista con los datos de cada postulante a la EAP"""
        postulantes = []
        for pag in pags:
            html = self.htmlContent(f'{self.__url}/{cod_sede_eap}/{pag}')
            if html.tbody is None:
                postulantes += []
            else:
                postulantes += self.__registrarPostulante(html.table.tbody)

        return postulantes


    def __registrarPostulante(self, body):
        """Obtiene los datos de cada postulante"""
        postulante = []
        
        for tr in body.find_all('tr'):
            postulante.append([info_postulante.text for info_postulante in tr.children])

        return postulante
