import os
import pandas as pd

class Resultados():

    def __init__(self, path):

        self.resultados = self.__dfRes(path)

    def __dfRes(self, path):
        """Crea el DataFrame principal"""
        listaArchivos = []

        for (dirpath, dirname, filenames) in os.walk(path):
            listaArchivos += [os.path.join(dirpath, archivo) for archivo in filenames]

        dframes = [pd.read_csv(csv) for csv in listaArchivos] 
        return pd.concat(dframes, ignore_index=True)

