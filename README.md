# SINIESTROWEB v4 — Mazda / MySQL

## Cambios de esta versión

- Base de datos alineada con `siniestro_web_v2`.
- Se agregó `orden` para controlar la posición del siniestro en el tablero.
- El semáforo se calcula automáticamente con **días hábiles** desde `fecha_actualizacion`:
  - 🟢 0–4 días
  - 🟡 5–11 días
  - 🔴 12+ días
- Los contadores de rojo, amarillo, verde, terminados y total se calculan directamente desde la información de MySQL.
- El tablero se actualiza automáticamente cada 60 segundos para volver a calcular los conteos.
- El estatus de taller se guarda en MySQL y el tablero cuenta los registros según el estatus seleccionado.
- Etapas disponibles:
  - Valuación
  - Autorización
  - Reserva
  - Esperando piezas
  - Citar
  - Citado
  - Colisión
- Cada cambio de etapa reinicia `fecha_estatus_taller`, por lo que también se puede saber cuántos días hábiles lleva el vehículo en esa etapa.
- El alta de siniestro permite seleccionar el estatus del taller desde la BD/lógica del sistema.
- Se mantiene CRUD y comentarios.

## Instalación

1. Instala MySQL y asegúrate de que el servidor esté en el puerto configurado.
2. Ejecuta `database.sql` completo en MySQL Workbench.
3. Verifica `.env` o las variables de entorno:
   - `MYSQL_HOST=localhost`
   - `MYSQL_PORT=3307` (cámbialo a 3306 si tu MySQL usa el puerto estándar)
   - `MYSQL_USER=root`
   - `MYSQL_PASSWORD=...`
   - `MYSQL_DATABASE=siniestro_web_v2`
4. Abre CMD/PowerShell en esta carpeta.
5. Instala dependencias:

```bat
py -m pip install -r requirements.txt
```

6. Ejecuta:

```bat
py app.py
```

7. Abre:

```text
http://127.0.0.1:5000/
```

## Si ya tenías una BD anterior

`migracion_siniestro_web_v2.sql` sirve como referencia para agregar `orden`, `fecha_estatus_taller` y las nuevas etapas. Haz respaldo antes de ejecutar migraciones sobre una base existente.

## Prueba rápida

Con `database.sql` recién instalado deben aparecer:

- SIN-001 → Valuación
- SIN-002 → Autorización
- SIN-003 → Reserva

El inicio debe mostrar los conteos correspondientes a esas etapas.


## Compatibilidad con una BD existente

Esta versión verifica al iniciar que `siniestros` tenga `orden`, `estatus_taller` y `fecha_estatus_taller`. Si alguna columna falta, la agrega sin borrar los registros existentes.

La información mostrada en el tablero, incluyendo No. de Siniestro, Orden, aseguradora, estatus del taller, semáforo y contadores, se obtiene directamente de MySQL.

Si prefieres hacerlo manualmente, ejecuta `migracion_semaforo_taller.sql` sobre `siniestro_web_v2`.


## Tipo de cliente: Particular / Aseguradora

El registro de siniestros ahora incluye `tipo_cliente`: `particular` o `aseguradora`.
- **Particular** queda seleccionado por defecto y el selector de aseguradoras se deshabilita; en MySQL `id_aseguradora` queda en `NULL`.
- **Aseguradora** habilita el selector, cuya lista se obtiene directamente de la tabla `aseguradoras`.
- Al actualizar un siniestro se puede cargar primero el registro desde MySQL con **Cargar**, conservando su tipo y aseguradora actuales.
- Para una BD existente puede ejecutarse `migracion_tipo_cliente.sql`; el sistema también intenta adaptar automáticamente la estructura al iniciar.
