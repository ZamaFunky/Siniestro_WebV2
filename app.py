import sys
from datetime import datetime, date
from flask import Flask, request, jsonify, redirect
from db_store import DBStore
from db import comments, add_comment, ensure_connection, ensure_schema
from clases.Siniestro import Siniestro, ESTATUS_TALLER
from pantallas.template_base import (
    get_css_link,
    get_header,
    get_footer,
    status_badge_html,
    siniestro_row_html,
    get_pending_followup_html,
    get_global_alert_banner_html,
    get_toast_notification_js,
)

app = Flask(__name__, static_folder="static", static_url_path="/static")

# =====================
# BASE EN MEMORIA (como atributo de la instancia Flask)
# =====================
app.SINIESTROS = DBStore()

# Verifica y adapta automáticamente una BD existente sin borrar sus datos.
try:
    ensure_schema()
except Exception as e:
    print("MySQL schema check:", e)


def siniestro_from_payload(payload: dict) -> Siniestro:
    fecha_raw = payload.get("fecha_actualizacion")
    return Siniestro(
        modelo=payload.get("modelo"),
        color=payload.get("color"),
        placas=payload.get("placas"),
        nosiniestro=payload.get("nosiniestro"),
        fecha_actualizacion=fecha_raw,
        orden=payload.get("orden", 0),
        aseguradora=payload.get("aseguradora"),
        tipo_cliente=payload.get("tipo_cliente") or ("aseguradora" if payload.get("aseguradora") else "particular"),
        terminado=payload.get("terminado", False),
        refacciones=payload.get("refacciones"),
        mano_obra=payload.get("mano_obra"),
        telefono=payload.get("telefono"),
        estatus_taller=payload.get("estatus_taller"),
        fecha_estatus_taller=payload.get("fecha_estatus_taller"),
    )


def serialize_siniestro(s: Siniestro):
    return {
        "modelo": s.get_modelo(),
        "color": s.get_color(),
        "placas": s.get_placas(),
        "nosiniestro": s.get_nosiniestro(),
        "orden": getattr(s, "orden", 0),
        "aseguradora": s.get_aseguradora(),
        "tipo_cliente": s.get_tipo_cliente(),
        "tipo_cliente_label": s.get_tipo_cliente_label(),
        "terminado": s.get_terminado(),
        "refacciones": s.get_refacciones(),
        "mano_obra": s.get_mano_obra(),
        "telefono": s.get_telefono(),
        "estatus_taller": s.get_estatus_taller(),
        "estatus_taller_label": s.get_estatus_taller_label(),
        "fecha_estatus_taller": s.get_fecha_estatus_taller_str(),
        "dias_en_estatus_taller": s.get_dias_en_estatus_taller(),
        "total": s.get_total(),
        "fecha_actualizacion": s.get_fecha_str(),
        "dias_desde_actualizacion": s.get_dias_desde_actualizacion(),
        "dias_habiles": s.get_dias_desde_actualizacion(),
        "status_color": s.get_status_color(),
        "status_emoji": s.get_status_emoji(),
        "status_label": s.get_status_label(),
    }


# ------------------------------------------------
# PAGINA PRINCIPAL - Menu Mazda
# ------------------------------------------------
@app.get("/")
@app.get("/inicio")
def home():
    # Se consulta MySQL en cada carga. Los colores se calculan con la fecha
    # actual, por lo que cambian automáticamente al pasar los días.
    siniestros = app.SINIESTROS
    registros = list(siniestros.values())

    total = len(registros)
    pendientes = [v for v in registros if not v.get("terminado")]

    green = sum(1 for v in pendientes if v.get("status_color") == "green")
    yellow = sum(1 for v in pendientes if v.get("status_color") == "yellow")
    red = sum(1 for v in pendientes if v.get("status_color") == "red")
    terminados = sum(1 for v in registros if v.get("terminado"))

    # Conteo de estatus del taller
    estatus_taller_counts = []
    for value, label in ESTATUS_TALLER:
        cantidad = sum(
            1 for v in pendientes
            if (v.get("estatus_taller") or "valuacion") == value
        )
        estatus_taller_counts.append((value, label, cantidad))

    green_por_vencer = sum(
        1 for v in pendientes
        if v.get("status_color") == "green"
        and v.get("dias_desde_actualizacion", 0) >= 3
    )
    total_pending = red + yellow + green_por_vencer

    pending_html = get_pending_followup_html(siniestros)
    alert_banner = get_global_alert_banner_html(red, yellow)
    toast_js = get_toast_notification_js(red, yellow, total_pending)

    # Tarjetas del estatus del taller
    taller_cards = ""
    taller_icons = {
        "valuacion": "📋",
        "autorizacion": "📝",
        "reserva": "🛒",
        "esperando_piezas": "⚙️",
        "citar": "📅",
        "citado": "✅",
        "colission": "💥",
    }
    for value, label, cantidad in estatus_taller_counts:
        icon = taller_icons.get(value, "🔧")
        taller_cards += f"""
        <div class="taller-status-card">
          <div class="taller-status-icon">{icon}</div>
          <div class="taller-status-info">
            <div class="taller-status-name">{label}</div>
            <div class="taller-status-count">{cantidad}</div>
            <div class="taller-status-caption">siniestro(s)</div>
          </div>
        </div>"""

    # Tablero operativo: muestra cada siniestro con su etapa actual y permite
    # cambiarla directamente desde el inicio.
    status_options = "".join(
        f'<option value="{value}">{label}</option>' for value, label in ESTATUS_TALLER
    )
    status_board_rows = ""
    for sin in pendientes:
        key = sin.get("nosiniestro", "")
        current = sin.get("estatus_taller") or "valuacion"
        opts = "".join(
            f'<option value="{value}"{" selected" if value == current else ""}>{label}</option>'
            for value, label in ESTATUS_TALLER
        )
        sc = sin.get("status_color", "green")
        status_board_rows += f"""
        <tr class="row-{sc}">
          <td><strong>{sin.get("orden",0)}</strong></td>
          <td><strong>{key}</strong><br><small>{sin.get("modelo","")} · {sin.get("placas","")}</small></td>
          <td>{status_badge_html(sc, sin.get("status_emoji","🟢"), sin.get("status_label","Al día"), sin.get("dias_desde_actualizacion",0))}</td>
          <td><strong>{sin.get("dias_desde_actualizacion",0)} día(s) hábil(es)</strong><br>
              <small>desde {sin.get("fecha_actualizacion","")}</small></td>
          <td>
            <form method="post" action="/actualizar-estatus/{key}" class="status-inline-form">
              <select name="estatus_taller" aria-label="Estatus de {key}">
                {opts}
              </select>
              <button type="submit" class="btn btn-primary btn-sm">💾 Actualizar</button>
            </form>
          </td>
        </tr>"""
    if not status_board_rows:
        status_board_rows = '<tr><td colspan="5" class="text-center" style="padding:2rem;color:#6b6b8a;">No hay siniestros pendientes.</td></tr>'

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mazda — Sistema de Siniestros</title>
  {get_css_link()}
</head>
<body>
{get_header("Sistema de Siniestros", active_page="inicio")}

<div class="mazda-container">

  {alert_banner}

  <!-- SEMÁFORO DE SINIESTROS -->
  <div class="mazda-card semaphore-card">
    <div class="semaphore-header">
      <div>
        <h2 style="margin-bottom:.25rem;">🚦 Semáforo de Siniestros</h2>
        <p style="color:#6b6b8a;margin:0;">
          Clasificación automática según días hábiles desde la última actualización.
        </p>
      </div>
      <span class="semaphore-date">Actualizado: {date.today().strftime("%d/%m/%Y")}</span>
    </div>

    <div class="semaphore-board">
      <div class="traffic-light">
        <div class="traffic-lamp red-lamp"></div>
        <div class="traffic-lamp yellow-lamp"></div>
        <div class="traffic-lamp green-lamp"></div>
        <div class="traffic-lamp blue-lamp"></div>
      </div>

      <div class="semaphore-counts">
        <div class="semaphore-count red-count">
          <span class="semaphore-number">{red}</span>
          <span class="semaphore-label">🔴 Urgentes</span>
          <small>12+ días hábiles</small>
        </div>
        <div class="semaphore-count yellow-count">
          <span class="semaphore-number">{yellow}</span>
          <span class="semaphore-label">🟡 Por vencer</span>
          <small>5 a 11 días hábiles</small>
        </div>
        <div class="semaphore-count green-count">
          <span class="semaphore-number">{green}</span>
          <span class="semaphore-label">🟢 Al día</span>
          <small>0 a 4 días hábiles</small>
        </div>
        <div class="semaphore-count blue-count">
          <span class="semaphore-number">{terminados}</span>
          <span class="semaphore-label">🔵 Terminados</span>
          <small></small>
        </div>
        <div class="semaphore-count blue-count">
          <span class="semaphore-number"></span>
          <span class="semaphore-label"></span>
          <small></small>
        </div>
        <div class="semaphore-count blue-count">
          <span class="semaphore-number">{total}</span>
          <span class="semaphore-label">🧮 Total De Siniestros</span>
          <small></small>
         </div>
      </div>
    </div>

    <div class="semaphore-total">
      Total pendientes: <strong>{len(pendientes)}</strong>
      &nbsp; | &nbsp;
      Terminados: <strong>{terminados}</strong>
      &nbsp; | &nbsp;
      Total registrados: <strong>{total}</strong>
    </div>
  </div>

  <!-- ESTATUS DEL TALLER -->
  <div class="mazda-card">
    <div class="semaphore-header">
      <div>
        <h2 style="margin-bottom:.25rem;">🔧 Estatus del Taller</h2>
        <p style="color:#6b6b8a;margin:0;">
          Cantidad de siniestros pendientes en cada etapa del taller.
        </p>
      </div>
      <a href="/siniestros" class="btn btn-outline btn-sm">Ver siniestros</a>
    </div>
    <div class="taller-status-grid">
      {taller_cards}
    </div>

    <div class="status-board-wrapper">
      <div class="status-board-title">
        <h3>📋 Tablero operativo</h3>
        <span>Actualiza la etapa de cada siniestro sin salir del tablero.</span>
      </div>
      <div style="overflow-x:auto;">
        <table class="mazda-table status-board-table">
          <thead>
            <tr>
              <th>Orden</th>
              <th>Siniestro</th>
              <th>Semáforo</th>
              <th>Días hábiles</th>
              <th>Estatus del taller</th>
            </tr>
          </thead>
          <tbody>{status_board_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  {pending_html}

  <div class="mazda-card">
    <h2>Resumen de Estados</h2>
    <p style="color:#6b6b8a; margin-bottom:1rem;">
      Los colores se recalculan automáticamente usando días hábiles: lunes a viernes, excluyendo festivos federales configurados.
    </p>
    <table class="mazda-table">
      <thead>
        <tr><th>Estado</th><th>Rango</th><th>Significado</th><th>Cantidad</th></tr>
      </thead>
      <tbody>
        <tr class="row-green">
          <td><span class="status-badge green">Al día</span></td>
          <td>0 - 4 días</td>
          <td>Actualización reciente</td>
          <td><strong>{green}</strong></td>
        </tr>
        <tr class="row-yellow">
          <td><span class="status-badge yellow">Por vencer</span></td>
          <td>5 - 11 días</td>
          <td>Requiere atención próxima</td>
          <td><strong>{yellow}</strong></td>
        </tr>
        <tr class="row-red">
          <td><span class="status-badge red">Urgente</span></td>
          <td>12+ días</td>
          <td>Requiere actualización inmediata</td>
          <td><strong>{red}</strong></td>
        </tr>
        <tr class="row-terminados">
          <td><span class="status-badge terminados">Terminados</span></td>
          <td>---</td>
          <td>Siniestros finalizados</td>
          <td><strong>{terminados}</strong></td>
        </tr>
      </tbody>
    </table>
  </div>

</div>

{get_footer()}
{toast_js}

<div style="margin-top:1rem;color:#6b6b8a;font-size:.9rem;">
  La fecha de seguimiento se registra manualmente al dar seguimiento a un siniestro.
  Los conteos se recalculan automáticamente con la información de la BD.
</div>
<script>setTimeout(function(){{ window.location.reload(); }}, 60000);</script>
</body>
</html>"""


@app.get("/ping")
def ping():
    return {"ok": True}


# ------------------------------------------------
# CRUD API JSON
# ------------------------------------------------
@app.post("/siniestro")
def crear_siniestro():
    data = request.get_json(silent=True) or {}
    sin = siniestro_from_payload(data)

    if sin.get_nosiniestro() is None:
        return jsonify({"error": "nosiniestro es obligatorio"}), 400

    if not sin.ValidarSiniestro():
        return jsonify({"error": "Datos invalidos"}), 400

    key = str(sin.get_nosiniestro())

    siniestros = app.SINIESTROS
    if key in siniestros:
        return jsonify({"error": "Ya existe un siniestro con ese nosiniestro"}), 409

    siniestros[key] = serialize_siniestro(sin)
    siniestros[key]["nosiniestro"] = key

    return jsonify({"mensaje": "Siniestro creado", "siniestro": siniestros[key]}), 201


@app.get("/siniestro/<nosiniestro>")
def consultar_siniestro(nosiniestro):
    key = str(nosiniestro)
    siniestros = app.SINIESTROS
    if key not in siniestros:
        return jsonify({"error": "Siniestro no encontrado"}), 404
    return jsonify(siniestros[key])


@app.put("/siniestro/<nosiniestro>")
def actualizar_siniestro(nosiniestro):
    key = str(nosiniestro)
    siniestros = app.SINIESTROS
    if key not in siniestros:
        return jsonify({"error": "Siniestro no encontrado"}), 404

    data = request.get_json(silent=True) or {}

    actualizado = dict(siniestros[key])
    for campo in ["orden", "tipo_cliente", "modelo", "color", "placas", "aseguradora", "terminado", "refacciones", "mano_obra", "telefono"]:
        if campo in data:
            actualizado[campo] = data[campo]

    if "estatus_taller" in data and data.get("estatus_taller"):
        if data.get("estatus_taller") not in {v for v, _ in ESTATUS_TALLER}:
            return jsonify({"error": "Estatus de taller no válido"}), 400
        actualizado["estatus_taller"] = data.get("estatus_taller")
        actualizado["fecha_estatus_taller"] = date.today().strftime("%Y-%m-%d")

    # Si el usuario envía una fecha, esa es la fecha real del seguimiento.
    # Si no la envía, se conserva la fecha existente.
    if "fecha_actualizacion" in data and data.get("fecha_actualizacion"):
        actualizado["fecha_actualizacion"] = data.get("fecha_actualizacion")

    sin = siniestro_from_payload(actualizado)
    if not sin.ValidarSiniestro():
        return jsonify({"error": "Datos invalidos"}), 400

    siniestros[key] = serialize_siniestro(sin)
    siniestros[key]["nosiniestro"] = key
    return jsonify({"mensaje": "Siniestro actualizado", "siniestro": siniestros[key]})



@app.post("/actualizar-estatus/<nosiniestro>")
def actualizar_estatus_taller_api(nosiniestro):
    key = str(nosiniestro)
    if key not in app.SINIESTROS:
        return redirect("/")
    estatus = str(request.form.get("estatus_taller", "")).strip()
    valores_validos = {v for v, _ in ESTATUS_TALLER}
    if estatus not in valores_validos:
        return redirect("/")
    # Cambiar etapa reinicia el contador de días de la etapa en MySQL.
    sin = dict(app.SINIESTROS[key])
    sin["estatus_taller"] = estatus
    sin["fecha_estatus_taller"] = date.today().strftime("%Y-%m-%d")
    app.SINIESTROS[key] = sin
    return redirect("/")

@app.delete("/siniestro/<nosiniestro>")
def eliminar_siniestro(nosiniestro):
    key = str(nosiniestro)
    siniestros = app.SINIESTROS
    if key not in siniestros:
        return jsonify({"error": "Siniestro no encontrado"}), 404
    eliminado = siniestros.pop(key)
    return jsonify({"mensaje": "Siniestro eliminado", "siniestro": eliminado})


# ------------------------------------------------
# MARCAR COMO TERMINADO / PENDIENTE
# ------------------------------------------------
@app.post("/marcar-terminado/<nosiniestro>")
def marcar_terminado(nosiniestro):
    key = str(nosiniestro)
    siniestros = app.SINIESTROS
    if key not in siniestros:
        return jsonify({"error": "Siniestro no encontrado"}), 404
    siniestros[key]["terminado"] = True
    return redirect(request.referrer or "/siniestros")


@app.post("/marcar-pendiente/<nosiniestro>")
def marcar_pendiente(nosiniestro):
    key = str(nosiniestro)
    siniestros = app.SINIESTROS
    if key not in siniestros:
        return jsonify({"error": "Siniestro no encontrado"}), 404
    siniestros[key]["terminado"] = False
    return redirect(request.referrer or "/siniestros")


# ------------------------------------------------
# ACTUALIZAR ESTATUS TALLER
# ------------------------------------------------
@app.post("/actualizar-estatus-taller/<nosiniestro>")
def actualizar_estatus_taller(nosiniestro):
    key = str(nosiniestro)
    siniestros = app.SINIESTROS
    if key not in siniestros:
        return jsonify({"error": "Siniestro no encontrado"}), 404

    nuevo_estatus = request.form.get("estatus_taller", "").strip()
    if not nuevo_estatus:
        return redirect(request.referrer or "/siniestros")

    # Update the status and the date
    siniestros[key]["estatus_taller"] = nuevo_estatus
    from clases.Siniestro import ESTATUS_TALLER
    label_map = dict(ESTATUS_TALLER)
    siniestros[key]["estatus_taller_label"] = label_map.get(nuevo_estatus, nuevo_estatus)
    siniestros[key]["fecha_estatus_taller"] = datetime.now().strftime("%Y-%m-%d")
    siniestros[key]["dias_en_estatus_taller"] = 0

    return redirect(request.referrer or "/siniestros")


# ------------------------------------------------
# VISTA DE SINIESTROS TERMINADOS
# ------------------------------------------------
@app.get("/siniestros-terminados")
def listar_terminados():
    siniestros = app.SINIESTROS
    terminados = {k: v for k, v in siniestros.items() if v.get("terminado")}

    rows_html = ""
    for sin in terminados.values():
        rows_html += siniestro_row_html(sin)

    if not rows_html:
        rows_html = '<tr><td colspan="12" class="text-center" style="padding:2rem;color:#6b6b8a;">No hay siniestros terminados. <a href="/siniestros" style="color:#e31837;">Ver todos</a></td></tr>'

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Siniestros Terminados — Mazda</title>
  {get_css_link()}
</head>
<body>
{get_header("Siniestros Terminados", active_page="terminados")}

<div class="mazda-container">
  <div class="mazda-card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">
      <h2 style="margin:0;border:none;padding:0;">Siniestros Terminados</h2>
      <a href="/siniestros" class="btn btn-outline btn-sm">Ver todos</a>
    </div>
    <div style="overflow-x:auto;">
      <table class="mazda-table">
        <thead>
          <tr>
            <th>No. Siniestro</th>
            <th>Orden</th>
            <th>Modelo</th>
            <th>Color</th>
            <th>Placas</th>
            <th>Cliente / Aseguradora</th>
            <th>Refacciones</th>
            <th>Mano Obra</th>
            <th>Total</th>
            <th>Ult. Actualizacion</th>
            <th>Estado</th>
            <th>Accion</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    <p class="mt-2 text-right" style="color:#6b6b8a;font-size:0.85rem;">
      Total: <strong>{len(terminados)}</strong> terminado(s)
    </p>
  </div>
</div>

{get_footer()}
</body>
</html>"""


# ------------------------------------------------
# VISTA DE TODOS LOS SINIESTROS
# ------------------------------------------------
@app.get("/siniestros")
def listar_siniestros():
    siniestros = app.SINIESTROS
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    if best == "application/json" or request.args.get("format") == "json":
        return jsonify(list(siniestros.values()))

    rows_html = ""
    for sin in siniestros.values():
        rows_html += siniestro_row_html(sin)

    if not rows_html:
        rows_html = '<tr><td colspan="12" class="text-center" style="padding:2rem;color:#6b6b8a;">No hay siniestros registrados. <a href="/NuevoSiniestro" style="color:#e31837;">Crear primero</a></td></tr>'

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Listado de Siniestros — Mazda</title>
  {get_css_link()}
</head>
<body>
{get_header("Listado de Siniestros", active_page="listar")}

<div class="mazda-container">
  <div class="mazda-card">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">
      <h2 style="margin:0;border:none;padding:0;">Todos los Siniestros</h2>
      <div>
        <a href="/siniestros-terminados" class="btn btn-success btn-sm">Terminados</a>
        <a href="/NuevoSiniestro" class="btn btn-primary btn-sm">Nuevo</a>
      </div>
    </div>
    <div style="overflow-x:auto;">
      <table class="mazda-table">
        <thead>
          <tr>
            <th>No. Siniestro</th>
            <th>Orden</th>
            <th>Modelo</th>
            <th>Color</th>
            <th>Placas</th>
            <th>Cliente / Aseguradora</th>
            <th>Refacciones</th>
            <th>Mano Obra</th>
            <th>Total</th>
            <th>Ult. Actualizacion</th>
            <th>Estado</th>
            <th>Accion</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    <p class="mt-2 text-right" style="color:#6b6b8a;font-size:0.85rem;">
      Total: <strong>{len(siniestros)}</strong> siniestro(s)
    </p>
  </div>
</div>

{get_footer()}
</body>
</html>"""


# ------------------------------------------------
# COMENTARIOS
# ------------------------------------------------
@app.get("/siniestro/<nosiniestro>/comentarios")
def listar_comentarios(nosiniestro):
    if nosiniestro not in app.SINIESTROS:
        return jsonify({"error": "Siniestro no encontrado"}), 404
    return jsonify(comments(nosiniestro))

@app.post("/siniestro/<nosiniestro>/comentarios")
def crear_comentario(nosiniestro):
    data=request.get_json(silent=True) or request.form
    texto=str(data.get("comentario","")).strip()
    if not texto:
        return jsonify({"error":"El comentario es obligatorio"}),400
    cid=add_comment(nosiniestro,texto)
    if cid is None: return jsonify({"error":"Siniestro no encontrado"}),404
    return jsonify({"mensaje":"Comentario agregado","id_comentario":cid}),201

@app.get("/estado-mysql")
def estado_mysql():
    return jsonify({"mysql": "conectado" if ensure_connection() else "desconectado"})

# ================================================
# IMPORTAR PANTALLAS (registran sus rutas al importar)
# ================================================
from pantallas import NuevoSiniestro  # noqa: E402, F401
from pantallas import MostrarSiniestro  # noqa: E402, F401
from pantallas import ActualizarSiniestro  # noqa: E402, F401
from pantallas import EliminarSiniestro  # noqa: E402, F401


# ================================================
# ENTRY POINT
# ================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)

