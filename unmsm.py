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
        try:
            response = requests.get(url)
            response.raise_for_status
        except HTTPError as http_err:
            return f'HTTP error ocurred: {http_err}'
        except Exception as err:
            return f'Error ocurred: {err}'
        else:
            return BeautifulSoup(response.content, "lxml")

    def getSedes(self):
        """Obtiene todas las sedes disponibles"""
        return [sede for sede in self.__sedes.keys()]

    def getEAPs(self, sede):
        """Obtiene todos los EAPs disponibles de acuerdo a la Sede"""
        return [eap for eap in self.__sedes[sede]]

    def exportarEap(self, sede, eap, path=None):
        """Exporta el csv correspondiente a la Sede y EAP"""
        cod_sede_eap = self.__sedes[sede.upper()][eap.upper()]
        index_escuela = self.htmlContent(f'{self.__url}/{cod_sede_eap}/0.html')
        if index_escuela.tfoot is None:
            pags = ['0.html']
        else:
            td_children = index_escuela.tfoot.tr.td.children
            pags = [a['href'] for a in td_children ]

        if path is None:
            self.__exportarCSV(self.__listarPostulantes(cod_sede_eap, pags), sede, eap)
        else:
            self.__exportarCSV(self.__listarPostulantes(cod_sede_eap, pags), sede, eap, path)


    def exportarTodo(self):
        """Exporta todos los datos de la página organizados por Sede"""
        try:
            os.mkdir(self.concurso)
            for sede in self.getSedes():
                os.makedirs(f'{self.concurso}/{sede}', exist_ok=True)
                for eap in self.getEAPs(sede):
                    root = self.concurso
                    subdir_sede = os.path.join(root, sede)
                    self.exportarEap(sede, eap, subdir_sede)
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


    def __exportarCSV(self, postulantes, sede, eap, path=None):
        """Exporta el archivo csv"""
        df = pd.DataFrame(postulantes)
        if path is None:
            df.to_csv(f'{self.concurso}-{sede}-{eap}.csv')
        else:
            df.to_csv(os.path.join(path, f'{self.concurso}-{sede}-{eap}.csv'))

    def __listarPostulantes(self, cod_sede_eap, pags):
        """Retorna una lista con los datos de todos los postulantes de la EAP"""
        postulantes = []
        for pag in pags:
            html = self.htmlContent(f'{self.__url}/{cod_sede_eap}/{pag}')
            if html.tbody is None:
                postulantes.append([])
            else:
                for tr in html.tbody.find_all('tr'):
                    postulantes.append(self.__registrarPostulante(tr))

        return postulantes

    def __registrarPostulante(self, tr):
        """Obtiene los datos de cada postulante"""
        postulante = {}
        td = [tag for tag in tr.children]
        postulante['SEDE'] = td[0].text
        postulante['CODIGO'] = td[1].text
        postulante['APELLIDOS Y NOMBRES'] = td[2].text
        postulante['E.P'] = td[2].text
        postulante['MERITO GENERAL'] = td[3].text
        postulante['MERITO SEDE'] = td[4].text
        postulante['MERITO EAP'] = td[5].text
        postulante['MERITO SEDE E.P'] = td[6].text
        postulante['OBSERVACION'] = td[7].text

        return postulante
