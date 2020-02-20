# unmsm-webscraping

Script para extraer los datos del simulacro de admisión de la UNMSM 2020-I 

## Instalar las librerias necesarias

```bash
pip install -r /path/to/requirements.txt
```

Si las librerias no se instalan correctamente  

```bash
pip install -r requirements.txt --no-index --find-links file://tmp/packages
```

## Data disponible

Fuente 1: [ResultSDP20201](http://unmsm.claro.net.pe/ResultSDP20201/index.html)
Fuente 2: [ResSimulacroPre](http://unmsm.claro.net.pe/ResSimulacroPre/index.html)

```
from unmsm import Unmsm
data = Unmsm('ResultSDP20201')
data.importarTodo() # Importará todos los resultados
```

## Contribuir

Pull requests bienvenidos. 
Para cambios importantes, abra primero un problema para analizar qué le gustaría cambiar.

Asegúrese de actualizar las pruebas según corresponda.
