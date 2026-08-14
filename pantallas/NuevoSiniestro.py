from flask import render_template_string, request, redirect
from datetime import datetime
from __main__ import app
from clases.Siniestro import Siniestro, ESTATUS_TALLER
from pantallas.template_base import get_css_link, get_header, get_footer, status_badge_html, get_aseguradora_select_html, get_estatus_taller_select_html

@app.get('/NuevoSiniestro')
def NuevoSiniestro():
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template_string("""<!doctype html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Nuevo Siniestro — Mazda</title>{{ css|safe }}</head>
<body>{{ header|safe }}
<div class="mazda-container"><div class="mazda-card">
<h2>Registrar Nuevo Siniestro</h2>
<form method="post" action="/nuevo-siniestro-form">
<div class="form-row">
<div class="form-group"><label>Modelo *</label><input name="modelo" placeholder="Ej: Mazda 3, CX-5" required></div>
<div class="form-group"><label>Color *</label><input name="color" placeholder="Ej: Rojo, Blanco" required></div>
</div>
<div class="form-row">
<div class="form-group"><label>Placas *</label><input name="placas" placeholder="Ej: ABC-123" required></div>
<div class="form-group"><label>No. de Siniestro *</label><input id="nosiniestro" name="nosiniestro" type="text" maxlength="50" autocomplete="off" placeholder="Ej: SIN-001" required></div>
</div>
<div class="form-row">
<div class="form-group"><label>Orden en tablero</label><input name="orden" type="number" min="0" value="0"></div>
<div class="form-group"><label>Fecha de actualización</label><input name="fecha_actualizacion" type="date" value="{{ today }}"></div>
</div>
<div class="form-row">
<div class="form-group">
<label for="tipo_cliente">Tipo de cliente *</label>
<select id="tipo_cliente" name="tipo_cliente" onchange="toggleAseguradora()" required>
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
<div class="form-group"><label>Teléfono del cliente</label><input name="telefono" type="tel" placeholder="Ej: 4271234567"></div>
<div class="form-row">
<div class="form-group"><label>Refacciones ($)</label><input name="refacciones" type="number" step="0.01" min="0" value="0"></div>
<div class="form-group"><label>Mano de obra ($)</label><input name="mano_obra" type="number" step="0.01" min="0" value="0"></div>
</div>
<div class="form-row">
<div class="form-group"><label for="estatus_taller">Estatus del taller *</label>{{ estatus_html|safe }}<small style="color:#6b6b8a;display:block;margin-top:.35rem;">Selecciona la etapa actual del vehículo.</small></div>
<div class="form-group"><label>Fecha de etapa</label><input name="fecha_estatus_taller" type="date" value="{{ today }}"></div>
</div>
<div class="btn-group"><button class="btn btn-primary" type="submit">➕ Guardar Siniestro</button><a href="/" class="btn btn-outline">← Volver</a></div>
</form>
<script>
function toggleAseguradora(){
  const tipo=document.getElementById('tipo_cliente');
  const select=document.getElementById('aseguradora');
  const help=document.getElementById('aseguradora-help');
  const esAseg=tipo && tipo.value==='aseguradora';
  select.disabled=!esAseg;
  select.required=esAseg;
  if(!esAseg) select.value='';
  help.textContent=esAseg ? 'Selecciona la aseguradora correspondiente.' : 'No aplica para cliente particular.';
}
toggleAseguradora();
</script>
</div></div>{{ footer|safe }}</body></html>""",
        css=get_css_link(), header=get_header("Nuevo Siniestro", "nuevo"), footer=get_footer(),
        today=today, aseguradora_html=get_aseguradora_select_html(),
        estatus_html=get_estatus_taller_select_html("valuacion"))

@app.post('/nuevo-siniestro-form')
def crear_form_siniestro():
    # Leemos explícitamente el formulario y normalizamos el número de siniestro.
    # Se aceptan también nombres alternos para evitar problemas con formularios
    # antiguos o caché del navegador.
    raw_no = (request.form.get('nosiniestro') or request.form.get('no_siniestro')
              or request.form.get('numero_siniestro') or request.form.get('numero') or '')
    no_siniestro = ' '.join(str(raw_no).strip().split()).upper()

    fields = {k: request.form.get(k) for k in [
        'modelo','color','placas','fecha_actualizacion','tipo_cliente','aseguradora',
        'refacciones','mano_obra','telefono','estatus_taller','fecha_estatus_taller','orden'
    ]}
    fields['nosiniestro'] = no_siniestro
    fields['tipo_cliente'] = 'aseguradora' if str(fields.get('tipo_cliente') or 'particular').strip().lower() == 'aseguradora' else 'particular'
    if fields['tipo_cliente'] == 'particular':
        fields['aseguradora'] = None
    errores=[]
    for k,label in [('modelo','Modelo'),('color','Color'),('placas','Placas'),('nosiniestro','No. Siniestro')]:
        value = fields.get(k)
        if value is None or not str(value).strip():
            errores.append(f"El campo {label} es obligatorio.")
    if fields['tipo_cliente'] == 'aseguradora' and not fields.get('aseguradora'):
        errores.append("Debes seleccionar una aseguradora.")
    valid_status={v for v,_ in ESTATUS_TALLER}
    if fields.get('estatus_taller') not in valid_status: errores.append("El estatus del taller no es válido.")
    if errores:
        return render_template_string("""<html><head>{{css|safe}}</head><body>{{header|safe}}<div class="mazda-container"><div class="mazda-card">
<div class="alert alert-error">{{mensaje}}</div><a href="/NuevoSiniestro" class="btn btn-outline">← Intentar de nuevo</a>
</div></div>{{footer|safe}}</body></html>""", css=get_css_link(),header=get_header("Nuevo Siniestro","nuevo"),footer=get_footer(),mensaje=" | ".join(errores))
    key=fields['nosiniestro']
    if not key:
        errores.append("El campo No. Siniestro es obligatorio.")
        return render_template_string("""<html><head>{{css|safe}}</head><body>{{header|safe}}<div class=\"mazda-container\"><div class=\"mazda-card\"><div class=\"alert alert-error\">{{mensaje}}</div><a href=\"/NuevoSiniestro\" class=\"btn btn-outline\">← Intentar de nuevo</a></div></div>{{footer|safe}}</body></html>""", css=get_css_link(),header=get_header("Nuevo Siniestro","nuevo"),footer=get_footer(),mensaje=" | ".join(errores))
    if key in app.SINIESTROS:
        return render_template_string("""<html><head>{{css|safe}}</head><body>{{header|safe}}<div class="mazda-container"><div class="mazda-card">
<div class="alert alert-error">Ya existe el siniestro <strong>{{key}}</strong>.</div><a href="/NuevoSiniestro" class="btn btn-outline">← Intentar con otro</a>
</div></div>{{footer|safe}}</body></html>""",css=get_css_link(),header=get_header("Nuevo Siniestro","nuevo"),footer=get_footer(),key=key)
    sin=Siniestro(
        modelo=fields['modelo'].strip(), color=fields['color'].strip(), placas=fields['placas'].strip(),
        nosiniestro=key, fecha_actualizacion=fields.get('fecha_actualizacion'), orden=fields.get('orden') or 0,
        aseguradora=fields.get('aseguradora'), tipo_cliente=fields.get('tipo_cliente'), refacciones=fields.get('refacciones') or 0,
        mano_obra=fields.get('mano_obra') or 0, telefono=fields.get('telefono'),
        estatus_taller=fields.get('estatus_taller'), fecha_estatus_taller=fields.get('fecha_estatus_taller'))
    if not sin.ValidarSiniestro():
        return redirect('/NuevoSiniestro')
    from app import serialize_siniestro
    app.SINIESTROS[key]=serialize_siniestro(sin)
    app.SINIESTROS[key]["nosiniestro"]=key
    badge=status_badge_html(sin.get_status_color(),sin.get_status_emoji(),sin.get_status_label(),sin.get_dias_desde_actualizacion())
    return render_template_string("""<html><head>{{css|safe}}</head><body>{{header|safe}}<div class="mazda-container"><div class="mazda-card">
<div class="alert alert-success">✅ Siniestro registrado correctamente.</div>
<table class="mazda-table"><tr><th>No. Siniestro</th><td><strong>{{key}}</strong></td></tr><tr><th>Modelo</th><td>{{modelo}}</td></tr>
<tr><th>Tipo de cliente</th><td>{{tipo_cliente}}</td></tr><tr><th>Aseguradora</th><td>{{aseguradora}}</td></tr><tr><th>Estatus del taller</th><td>{{estatus}}</td></tr><tr><th>Semáforo</th><td>{{badge|safe}}</td></tr></table>
<div class="btn-group"><a href="/" class="btn btn-primary">Ir al inicio</a><a href="/NuevoSiniestro" class="btn btn-secondary">Nuevo</a></div>
</div></div>{{footer|safe}}</body></html>""",css=get_css_link(),header=get_header("Nuevo Siniestro","nuevo"),footer=get_footer(),
        key=key,modelo=sin.get_modelo(),tipo_cliente=sin.get_tipo_cliente_label(),aseguradora=(sin.get_aseguradora() if sin.get_tipo_cliente()=="aseguradora" else "No aplica"),
        estatus=sin.get_estatus_taller_label(),badge=badge)
