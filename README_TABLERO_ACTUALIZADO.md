# Tablero de Siniestros Mazda

## Semáforo automático

El tablero consulta MySQL y recalcula los días hábiles desde `fecha_actualizacion`:

- 🟢 **Al día:** 0 a 4 días hábiles.
- 🟡 **Por vencer:** 5 a 11 días hábiles.
- 🔴 **Urgente:** 12 o más días hábiles.
- 🔵 **Terminados:** vehículos marcados como terminados.

Los contadores de cada color se generan con los registros reales de la BD. El inicio se recarga cada 60 segundos para mantener la información actualizada.

## Estatus del taller

El estatus se guarda en `siniestros.estatus_taller` y el tablero cuenta cuántos vehículos están en cada etapa:

1. Valuación
2. Autorización
3. Reserva
4. Esperando piezas
5. Citar
6. Citado
7. Colisión

Al cambiar de etapa se actualiza `fecha_estatus_taller`. El sistema calcula también los días hábiles que el vehículo lleva en esa etapa.

## Base de datos

La BD utilizada por esta versión es `siniestro_web_v2` y el esquema completo está en `database.sql`.

Si existe una instalación anterior, respáldala antes de ejecutar migraciones.
