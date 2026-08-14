SINIESTROWEB - MYSQL

1. Instala MySQL Server y MySQL Workbench.
2. Abre database.sql en Workbench y ejecútalo.
3. En la carpeta del proyecto ejecuta:
   py -m venv env
   env\Scripts\activate
   pip install -r requirements.txt
4. Copia .env.example como .env si quieres documentar la configuración.
5. Configura MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD y MYSQL_DATABASE
   como variables de entorno (por defecto usa localhost/root/siniestroweb).
6. Ejecuta:
   python app.py
7. Abre http://127.0.0.1:5000

El proyecto ya usa MySQL para altas, consultas, actualizaciones, eliminaciones,
estatus, terminados y comentarios. Los comentarios se manejan con:
GET  /siniestro/<nosiniestro>/comentarios
POST /siniestro/<nosiniestro>/comentarios
JSON: {"comentario":"Texto"}

IMPORTANTE: no se incluye el entorno virtual para mantener el ZIP ligero.


CAMBIO: La fecha_actualizacion es la fecha manual del último seguimiento. Se eliminó la recarga automática diaria del dashboard. Para registrar seguimiento, usa Actualizar Siniestro y captura la fecha real.
