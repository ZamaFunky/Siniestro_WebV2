#ACTIVAR ENTORNO VIRTUAL
#py -m venv env
#env\Scripts\activate

from flask import Flask, render_template_string, request

app = Flask(__name__)

MENU_HTML = """<!doctype html>
<html lang='es'>
<body>
<h1>Sistema de Siniestros</h1>
<ul>
<li><a href='/NuevoSiniestro'>Nuevo Siniestro</a></li>
<li><a href='/ConsultarSiniestro'>Consultar</a></li>
<li><a href='/ActualizarSiniestro'>Actualizar</a></li>
<li><a href='/EliminarSiniestro'>Eliminar</a></li>
<li><a href='/siniestros'>Listar</a></li>
</ul>
</body>
</html>"""

@app.get('/index')
@app.get('/inicio')
def inicio():
    return render_template_string(MENU_HTML)

# IMPORTAR MÓDULOS DE PANTALLAS (registran sus rutas al importar)
from pantallas import NuevoSiniestro  # noqa: F401
from pantallas import MostrarSiniestro  # noqa: F401
from pantallas import ActualizarSiniestro  # noqa: F401
from pantallas import EliminarSiniestro  # noqa: F401


if __name__ == '__main__':
    app.run(debug=True, port=5000)



