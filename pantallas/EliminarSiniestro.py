from flask import render_template_string, request

from __main__ import app
from pantallas.template_base import (
    get_css_link,
    get_header,
    get_footer,
    status_badge_html,
    siniestro_row_html,
) 


@app.get('/EliminarSiniestro')
def EliminarSiniestro():
    return render_template_string("""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Eliminar Siniestro — Mazda</title>
  {{ css|safe }}
</head>
<body>
{{ header|safe }}

<div class="mazda-container">
  <div class="mazda-card">
    <h2>Eliminar Siniestro</h2>
    <div class="alert alert-error" style="margin-bottom:1.5rem;">
      &#x26A0;&#xFE0F; Esta acci&oacute;n es irreversible. Una vez eliminado, el registro no podr&aacute; recuperarse.
    </div>
    <form method='post' action='/eliminar-siniestro'>
      <div class="form-group">
        <label for="nosiniestro">No. Siniestro a eliminar *</label>
        <input id="nosiniestro" name="nosiniestro" type="text" placeholder="Ej: SIN-001" required>
      </div>
      <div class="btn-group">
        <button type="submit" class="btn btn-danger">&#x1F5D1; Eliminar Siniestro</button>
        <a href="/" class="btn btn-outline">&#x2190; Cancelar y volver</a>
      </div>
    </form>
  </div>

  <!-- Vista previa de todos los registros para ayudar a identificar -->
  <div class="mazda-card">
    <h3>Registros actuales</h3>
    <div style="overflow-x:auto;">
      <table class="mazda-table">
        <thead>
          <tr>
            <th>No. Siniestro</th>
            <th>Modelo</th>
            <th>Color</th>
            <th>Placas</th>
            <th>Aseguradora</th>
            <th>&Uacute;lt. Actualizaci&oacute;n</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {{ rows|safe }}
        </tbody>
      </table>
    </div>
  </div>
</div>

{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer(),
           rows=_get_all_rows())


def _get_all_rows():
    """Helper to build the preview table rows."""
    siniestros_mem = getattr(app, 'SINIESTROS', {})
    if not siniestros_mem:
        return """<tr><td colspan="7" class="text-center" style="padding:2rem;color:#6b6b8a;">
          No hay siniestros registrados.
        </td></tr>"""
    rows = ""
    for sin in siniestros_mem.values():
        rows += siniestro_row_html(sin)
    return rows


@app.post('/eliminar-siniestro')
def eliminar_form_siniestro():
    nos = request.form.get('nosiniestro')
    key = str(nos).strip() if nos is not None else ''

    if key == '':
        return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-error">El n&uacute;mero de siniestro es obligatorio.</div>
    <a href="/EliminarSiniestro" class="btn btn-outline">&larr; Intentar de nuevo</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer())

    if not hasattr(app, 'SINIESTROS'):
        return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-error">Error: Backend no inicializado.</div>
    <a href="/" class="btn btn-outline">&larr; Volver</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer())

    if key not in app.SINIESTROS:
        return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-error">
      No se encontr&oacute; ning&uacute;n siniestro con el n&uacute;mero <strong>{{ key }}</strong>.
    </div>
    <a href="/EliminarSiniestro" class="btn btn-outline">&larr; Intentar con otro n&uacute;mero</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer(), key=key)

    # Mostrar datos del siniestro antes de eliminarlo
    sin_data = app.SINIESTROS[key]
    sc = sin_data.get("status_color", "green")
    badge = status_badge_html(
        sc,
        sin_data.get("status_emoji", "\U0001f7e2"),
        sin_data.get("status_label", "Al d\u00eda"),
        sin_data.get("dias_desde_actualizacion", 0),
    )

    return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <h2>Confirmar Eliminaci&oacute;n</h2>
    <div class="alert alert-error" style="margin-bottom:1.5rem;">
      &#x26A0;&#xFE0F; Est&aacute; a punto de eliminar el siguiente siniestro. Esta acci&oacute;n no se puede deshacer.
    </div>

    <table class="mazda-table">
      <thead><tr><th>Campo</th><th>Valor</th></tr></thead>
      <tbody>
        <tr><td>No. Siniestro</td><td><strong>{{ key }}</strong></td></tr>
        <tr><td>Modelo</td><td>{{ modelo }}</td></tr>
        <tr><td>Color</td><td>{{ color }}</td></tr>
        <tr><td>Placas</td><td>{{ placas }}</td></tr>
        <tr><td>&Uacute;lt. Actualizaci&oacute;n</td><td>{{ fecha }}</td></tr>
        <tr><td>Estado</td><td>{{ badge|safe }}</td></tr>
      </tbody>
    </table>

    <form method='post' action='/confirmar-eliminar-siniestro' style="margin-top:1.5rem;">
      <input type="hidden" name="nosiniestro" value="{{ key }}">
      <div class="btn-group">
        <button type="submit" class="btn btn-danger">&#x1F5D1; S&iacute;, eliminar permanentemente</button>
        <a href="/" class="btn btn-outline">&#x2190; No, cancelar</a>
      </div>
    </form>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer(), key=key,
           modelo=sin_data.get("modelo", ""),
           color=sin_data.get("color", ""),
           placas=sin_data.get("placas", ""),
           fecha=sin_data.get("fecha_actualizacion", ""),
           badge=badge)


@app.post('/confirmar-eliminar-siniestro')
def confirmar_eliminar():
    nos = request.form.get('nosiniestro')
    key = str(nos).strip() if nos is not None else ''

    if key == '' or key not in app.SINIESTROS:
        return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-error">El siniestro <strong>{{ key }}</strong> ya no existe o no es v&aacute;lido.</div>
    <a href="/" class="btn btn-outline">&larr; Volver al inicio</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer(), key=key)

    eliminado = app.SINIESTROS.pop(key)

    return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-success">
      &#x2705; Siniestro <strong>{{ key }}</strong> eliminado permanentemente.
    </div>
    <div class="btn-group">
      <a href="/" class="btn btn-primary">&#x2190; Ir al inicio</a>
      <a href="/EliminarSiniestro" class="btn btn-danger">&#x1F5D1; Eliminar otro</a>
    </div>
  </div>
</div>
{{ footer|safe }}
<script>setTimeout(() => { window.location = '/'; }, 4000);</script>
</body>
</html>""", css=get_css_link(), header=get_header("Eliminar Siniestro", active_page="eliminar"),
           footer=get_footer(), key=key)

