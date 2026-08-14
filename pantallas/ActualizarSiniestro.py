from flask import render_template_string, request
from datetime import datetime, date

from __main__ import app
from clases.Siniestro import Siniestro
from pantallas.template_base import (
    get_css_link,
    get_header,
    get_footer,
    status_badge_html,
    get_aseguradora_select_html,
    get_estatus_taller_select_html,
)


@app.get('/ActualizarSiniestro')
def ActualizarSiniestro():
    return render_template_string("""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Actualizar Siniestro — Mazda</title>
  {{ css|safe }}
</head>
<body>
{{ header|safe }}

<div class="mazda-container">
  <div class="mazda-card">
    <h2>Actualizar Siniestro Existente</h2>
    <p style="color:#6b6b8a; margin-bottom:1.5rem;">
      Ingrese el n&uacute;mero de siniestro y los nuevos datos. La fecha de seguimiento se captura manualmente para saber exactamente qu&eacute; d&iacute;a se dio seguimiento.
    </p>
    <form method='post' action='/actualizar-siniestro'>
      <div class="form-group">
        <label for="nosiniestro">No. Siniestro (a actualizar) *</label>
        <div style="display:flex;gap:.5rem;align-items:center;">
          <input id="nosiniestro" name="nosiniestro" type="text" placeholder="Ej: SIN-001" required style="flex:1;">
          <button type="button" class="btn btn-outline btn-sm" onclick="cargarSiniestro()">🔎 Cargar</button>
        </div>
        <small id="carga-mensaje" style="color:#6b6b8a;display:block;margin-top:.35rem;">Escribe el número y pulsa Cargar para traer lo que ya existe en MySQL.</small>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="modelo">Nuevo Modelo *</label>
          <input id="modelo" name="modelo" placeholder="Ej: Mazda CX-30" required>
        </div>
        <div class="form-group">
          <label for="color">Nuevo Color *</label>
          <input id="color" name="color" placeholder="Ej: Azul" required>
        </div>
      </div>
      <div class="form-group">
        <label for="placas">Nuevas Placas *</label>
        <input id="placas" name="placas" placeholder="Ej: XYZ-9876" required>
      </div>
      <div class="form-group">
        <label for="fecha_actualizacion">Fecha de seguimiento / actualizaci&oacute;n *</label>
        <input id="fecha_actualizacion" name="fecha_actualizacion" type="date" value="{{ today }}" required>
        <small style="color:#6b6b8a;">Indica el d&iacute;a en que realmente se dio seguimiento al siniestro.</small>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="refacciones">Refacciones ($)</label>
          <input id="refacciones" name="refacciones" type="number" step="0.01" min="0" placeholder="Ej: 1500.00">
        </div>
        <div class="form-group">
          <label for="mano_obra">Mano de Obra ($)</label>
          <input id="mano_obra" name="mano_obra" type="number" step="0.01" min="0" placeholder="Ej: 800.50">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="tipo_cliente">Tipo de cliente *</label>
          <select id="tipo_cliente" name="tipo_cliente" onchange="toggleAseguradoraActualizar()" required>
            <option value="particular" selected>Particular</option>
            <option value="aseguradora">Aseguradora</option>
          </select>
          <small style="color:#6b6b8a;display:block;margin-top:.35rem;">Particular viene seleccionado por defecto.</small>
        </div>
        <div class="form-group">
          <label for="aseguradora">Aseguradora</label>
          {{ aseguradora_html|safe }}
          <small id="aseguradora-help" style="color:#6b6b8a;display:block;margin-top:.35rem;">No aplica para cliente particular.</small>
        </div>
      </div>
      <div class="form-group">
        <label for="telefono">Tel&eacute;fono del cliente</label>
        <input id="telefono" name="telefono" type="tel" placeholder="Ej: 55-1234-5678">
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="orden">Orden en tablero</label>
          <input id="orden" name="orden" type="number" min="0" value="0">
        </div>
        <div class="form-group">
          <label for="estatus_taller">Estatus del taller</label>
          {{ estatus_html|safe }}
        </div>
      </div>
      <div class="btn-group">
        <button type="submit" class="btn btn-primary">&#x270F;&#xFE0F; Actualizar Siniestro</button>
        <a href="/" class="btn btn-outline">&#x2190; Volver</a>
      </div>
    </form>
    <script>
    async function cargarSiniestro(){
      const no=document.getElementById('nosiniestro').value.trim().toUpperCase();
      const msg=document.getElementById('carga-mensaje');
      if(!no){ msg.textContent='Escribe primero el No. de Siniestro.'; msg.style.color='#c0392b'; return; }
      try{
        const r=await fetch('/siniestro/'+encodeURIComponent(no));
        const data=await r.json();
        if(!r.ok){ msg.textContent=data.error || 'No se encontró el siniestro.'; msg.style.color='#c0392b'; return; }
        const set=(id,val)=>{const e=document.getElementById(id); if(e && val!==undefined && val!==null) e.value=val;};
        set('modelo',data.modelo); set('color',data.color); set('placas',data.placas);
        set('fecha_actualizacion',data.fecha_actualizacion); set('refacciones',data.refacciones); set('mano_obra',data.mano_obra);
        set('telefono',data.telefono || ''); set('orden',data.orden ?? 0); set('estatus_taller',data.estatus_taller || 'valuacion');
        set('tipo_cliente',data.tipo_cliente || 'particular'); set('aseguradora',data.aseguradora || '');
        toggleAseguradoraActualizar();
        if(data.aseguradora) set('aseguradora',data.aseguradora);
        msg.textContent='✓ Datos cargados desde MySQL. Puedes modificarlos y guardar.'; msg.style.color='#188038';
      }catch(e){ msg.textContent='No fue posible consultar MySQL.'; msg.style.color='#c0392b'; }
    }
    function toggleAseguradoraActualizar(){
      const tipo=document.getElementById('tipo_cliente');
      const select=document.getElementById('aseguradora');
      const help=document.getElementById('aseguradora-help');
      const esAseg=tipo && tipo.value==='aseguradora';
      select.disabled=!esAseg;
      select.required=esAseg;
      if(!esAseg) select.value='';
      help.textContent=esAseg ? 'Selecciona la aseguradora correspondiente.' : 'No aplica para cliente particular.';
    }
    toggleAseguradoraActualizar();
    </script>
  </div>
</div>

{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Actualizar Siniestro", active_page="actualizar"),
           footer=get_footer(),
           today=date.today().strftime("%Y-%m-%d"),
           aseguradora_html=get_aseguradora_select_html(), estatus_html=get_estatus_taller_select_html())


@app.post('/actualizar-siniestro')
def actualizar_form_siniestro():
    nos = request.form.get('nosiniestro')
    key = str(nos).strip() if nos is not None else ''

    # Validaciones
    errores = []
    if key == '':
        errores.append("El n&uacute;mero de siniestro es obligatorio.")
    if not hasattr(app, 'SINIESTROS'):
        errores.append("Error: Backend no inicializado.")

    if errores:
        return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-error">{{ mensaje }}</div>
    <a href="/ActualizarSiniestro" class="btn btn-outline">&larr; Intentar de nuevo</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Actualizar Siniestro", active_page="actualizar"),
           footer=get_footer(), mensaje=" | ".join(errores))

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
    <a href="/ActualizarSiniestro" class="btn btn-outline">&larr; Intentar con otro n&uacute;mero</a>
    <a href="/ConsultarSiniestro" class="btn btn-secondary">Consultar registros</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Actualizar Siniestro", active_page="actualizar"),
           footer=get_footer(), key=key)

    modelo = request.form.get('modelo')
    color = request.form.get('color')
    placas = request.form.get('placas')
    tipo_cliente = request.form.get('tipo_cliente') or 'particular'
    tipo_cliente = 'aseguradora' if tipo_cliente.strip().lower() == 'aseguradora' else 'particular'
    aseguradora = request.form.get('aseguradora') if tipo_cliente == 'aseguradora' else None
    if tipo_cliente == 'aseguradora' and not aseguradora:
        return render_template_string('''<!doctype html><html lang="es"><head><meta charset="UTF-8">{{ css|safe }}</head><body>{{ header|safe }}<div class="mazda-container"><div class="mazda-card"><div class="alert alert-error">Debes seleccionar una aseguradora cuando el tipo de cliente es Aseguradora.</div><a href="/ActualizarSiniestro" class="btn btn-outline">&larr; Intentar de nuevo</a></div></div>{{ footer|safe }}</body></html>''', css=get_css_link(), header=get_header('Actualizar Siniestro','actualizar'), footer=get_footer())
    refacciones = request.form.get('refacciones')
    mano_obra = request.form.get('mano_obra')
    telefono = request.form.get('telefono')
    fecha_actualizacion = request.form.get('fecha_actualizacion')
    orden = request.form.get('orden') or 0
    estatus_taller = request.form.get('estatus_taller') or 'valuacion'

    sin = Siniestro(
        modelo=modelo,
        color=color,
        placas=placas,
        nosiniestro=key,
        fecha_actualizacion=fecha_actualizacion,
        orden=orden,
        estatus_taller=estatus_taller,
        tipo_cliente=tipo_cliente,
        fecha_estatus_taller=date.today().strftime("%Y-%m-%d"),
        aseguradora=aseguradora,
        refacciones=refacciones if refacciones else None,
        mano_obra=mano_obra if mano_obra else None,
        telefono=telefono if telefono else None,
    )

    if not sin.ValidarSiniestro():
        return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-error">Datos inv&aacute;lidos. Verifica que todos los campos est&eacute;n completos.</div>
    <a href="/ActualizarSiniestro" class="btn btn-outline">&larr; Intentar de nuevo</a>
  </div>
</div>
{{ footer|safe }}
</body>
</html>""", css=get_css_link(), header=get_header("Actualizar Siniestro", active_page="actualizar"),
           footer=get_footer())

    from app import serialize_siniestro as serialize
    app.SINIESTROS[key] = serialize(sin)
    app.SINIESTROS[key]["nosiniestro"] = key

    badge = status_badge_html(
        sin.get_status_color(),
        sin.get_status_emoji(),
        sin.get_status_label(),
        sin.get_dias_desde_actualizacion(),
    )

    return render_template_string("""<!doctype html>
<html lang="es">
<head><meta charset="UTF-8">{{ css|safe }}</head>
<body>
{{ header|safe }}
<div class="mazda-container">
  <div class="mazda-card">
    <div class="alert alert-success">&#x2705; Siniestro <strong>{{ key }}</strong> actualizado con &eacute;xito.</div>
    <p style="color:#6b6b8a; margin-bottom:1rem;">Fecha de seguimiento registrada: <strong>{{ fecha_actualizacion }}</strong></p>
    <table class="mazda-table">
      <thead><tr><th>Campo</th><th>Valor</th></tr></thead>
      <tbody>
        <tr><td>No. Siniestro</td><td><strong>{{ key }}</strong></td></tr>
        <tr><td>Modelo</td><td>{{ modelo }}</td></tr>
        <tr><td>Color</td><td>{{ color }}</td></tr>
        <tr><td>Placas</td><td>{{ placas }}</td></tr>
        <tr><td>Tipo de cliente</td><td>{{ tipo_cliente_label }}</td></tr>
        <tr><td>Aseguradora</td><td>{{ aseguradora_label }}</td></tr>
        <tr><td>Estado</td><td>{{ badge|safe }}</td></tr>
      </tbody>
    </table>
    <div class="btn-group">
      <a href="/" class="btn btn-primary">&#x2190; Ir al inicio</a>
      <a href="/ActualizarSiniestro" class="btn btn-secondary">&#x270F;&#xFE0F; Actualizar otro</a>
    </div>
  </div>
</div>
{{ footer|safe }}
<script>setTimeout(() => { window.location = '/'; }, 4000);</script>
</body>
</html>""", css=get_css_link(), header=get_header("Actualizar Siniestro", active_page="actualizar"),
           footer=get_footer(), key=key, modelo=sin.get_modelo(), color=sin.get_color(),
           fecha_actualizacion=sin.get_fecha_str(),
           placas=sin.get_placas(), badge=badge,
           tipo_cliente_label=sin.get_tipo_cliente_label(),
           aseguradora_label=sin.get_aseguradora() if sin.get_aseguradora() else "Particular / No aplica")

