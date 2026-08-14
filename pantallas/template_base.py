"""
Shared HTML components for the Mazda Siniestros System.
Provides header, footer, CSS link, and status badge generators.
"""

# Mazda Logo (image from URL)
MAZDA_LOGO_IMG = '<img src="https://pngimg.com/uploads/car_logo/car_logo_PNG1654.png" alt="Mazda Logo" style="height:40px;width:auto;vertical-align:middle;">'


def get_css_link():
    """Return the <link> tag for the Mazda stylesheet."""
    return '<link rel="stylesheet" href="/static/css/mazda.css">'


def get_aseguradora_select_html(selected="", disabled=False):
    """Lista de aseguradoras tomada directamente de MySQL."""
    try:
        from db import get_aseguradoras
        aseguradoras = get_aseguradoras()
    except Exception:
        aseguradoras = []
    opts = '  <option value="">Seleccionar aseguradora...</option>\n'
    for row in aseguradoras:
        value = row.get("nombre", "")
        sel = ' selected' if str(value) == str(selected) else ''
        opts += f'  <option value="{value}"{sel}>{value}</option>\n'
    dis = ' disabled' if disabled else ''
    return f'<select id="aseguradora" name="aseguradora"{dis}>\n{opts}</select>'


def get_estatus_taller_select_html(selected=""):
    """Return HTML for a <select> dropdown of taller statuses."""
    from clases.Siniestro import ESTATUS_TALLER
    opts = ""
    for value, label in ESTATUS_TALLER:
        sel = ' selected' if str(value) == str(selected) else ''
        opts += f'  <option value="{value}"{sel}>{label}</option>\n'
    return f'<select id="estatus_taller" name="estatus_taller" class="estatus-select">\n{opts}</select>'


def get_estatus_taller_badge(estatus_taller):
    """Return a small badge for the taller status."""
    mapping = {
        "valuacion": ("valuacion", "\U0001f4cb", "En valuaci\u00f3n"),
        "autorizacion": ("autorizacion", "\U0001f4dd", "En autorizaci\u00f3n"),
        "reserva": ("reserva", "\U0001f6cd\ufe0f", "En reserva"),
        "esperando_piezas": ("piezas", "\u2699\ufe0f", "Esperando piezas"),
        "colission": ("colission", "\U0001f4a5", "Colission"),
    }
    cls, emoji, label = mapping.get(estatus_taller, ("", "", ""))
    if not cls:
        return '<span class="status-badge" style="background:#f0f0f5;color:#6b6b8a;font-size:0.72rem;">Sin estatus</span>'
    return f'<span class="status-badge {cls}" style="font-size:0.72rem;">{emoji} {label}</span>'


def get_header(title="Sistema de Siniestros", active_page=""):
    """Return the full Mazda-themed <header> block."""
    nav_items = {
        "nuevo":      ("/NuevoSiniestro",      "\U0001f4dd Nuevo"),
        "consultar":  ("/ConsultarSiniestro",   "\U0001f50e Consultar"),
        "actualizar": ("/ActualizarSiniestro",  "\U0001f504 Actualizar"),
        "eliminar":   ("/EliminarSiniestro",    "\u274c Eliminar"),
        "listar":     ("/siniestros",           "\U0001f4c1 Listar"),
        "terminados": ("/siniestros-terminados", "\U0001f3c1 Terminados"),
    }

    nav_html = ""
    for slug, (href, label) in nav_items.items():
        active_class = ' class="active"' if slug == active_page else ""
        nav_html += f'<a href="{href}"{active_class}>{label}</a>\n'

    inicio_active = ' class="active"' if active_page == "inicio" else ""

    return f"""<header class="mazda-header">
  <div class="logo-area">
    {MAZDA_LOGO_IMG}
    <h1><span>\u25cf</span> {title}</h1>
  </div>
  <nav class="nav-links">
    <a href="/"{inicio_active}>\U0001f3e0 Inicio</a>
    {nav_html}
  </nav>
</header>"""


def get_footer():
    """Return the Mazda-themed footer block."""
    return """<footer class="mazda-footer">
  &copy; 2025 <span>Mazda</span> &mdash; Sistema de Gesti&oacute;n de Siniestros &bull; Todos los derechos reservados
</footer>"""


def status_badge_html(status_color, emoji, label, dias):
    """Return HTML for a coloured status badge."""
    return f"""<span class="status-badge {status_color}">
  {emoji} {label} ({dias} d&iacute;as)
</span>"""


# ============================================================
# NOTIFICATIONS & ALERTS COMPONENTS
# ============================================================

def get_pending_followup_html(siniestros_dict):
    """
    Generate HTML for the "Pendientes de Seguimiento · Días hábiles" section.
    Shows siniestros that need attention grouped by urgency:
      - Red (urgent, 12+ días hábiles): "¡URGENTE! Sin actualizar"
      - Yellow (warning, 5-11 días hábiles): "Próximo a vencer"
      - Green (info, >= 3 días hábiles): "Por vencer pronto"
    """
    urgent_items = []   # red
    warning_items = []  # yellow
    upcoming_items = [] # green with >= 3 días hábiles

    for sin in siniestros_dict.values():
        if sin.get("terminado", False):
            continue
        sc = sin.get("status_color", "green")
        dias = sin.get("dias_desde_actualizacion", 0)
        key = sin.get("nosiniestro", "")

        if sc == "red":
            urgent_items.append(sin)
        elif sc == "yellow":
            warning_items.append(sin)
        elif sc == "green" and dias >= 3:
            upcoming_items.append(sin)

    total_pending = len(urgent_items) + len(warning_items) + len(upcoming_items)
    if total_pending == 0:
        return ""

    def _item_html(sin, css_class, icon, badge_text, badge_class, message):
        key = sin.get("nosiniestro", "")
        modelo = sin.get("modelo", "")
        placas = sin.get("placas", "")
        dias = sin.get("dias_desde_actualizacion", 0)
        aseguradora = sin.get("aseguradora", "N/A")
        return f"""<div class="pending-item {css_class}">
  <div class="pending-icon">{icon}</div>
  <div class="pending-info">
    <div class="pending-title">{key} — {modelo}</div>
    <div class="pending-meta">Placas: {placas} &bull; Aseguradora: {aseguradora} &bull; {dias} d\u00eda(s) sin actualizar</div>
  </div>
  <span class="pending-badge {badge_class}">{badge_text}</span>
  <a href="/ActualizarSiniestro" class="pending-action">Actualizar</a>
</div>"""

    items_html = ""

    # Urgent items (red)
    for sin in urgent_items:
        items_html += _item_html(
            sin, "urgent", "\U0001f534",
            "\u00a1URGENTE!", "red",
            "Requiere actualizaci\u00f3n inmediata"
        )

    # Warning items (yellow)
    for sin in warning_items:
        items_html += _item_html(
            sin, "warning", "\u26a0\ufe0f",
            "Por vencer", "yellow",
            "Requiere atenci\u00f3n pr\u00f3xima"
        )

    # Upcoming items (green >= 3 días hábiles)
    for sin in upcoming_items:
        items_html += _item_html(
            sin, "info", "\U0001f4c5",
            "Actualiza pronto", "green",
            "Por vencer pronto"
        )

    # Emotional / urgency message based on what's pending
    if urgent_items:
        header_icon = "\U0001f6a8"
        nos_list = " ".join(s.get("nosiniestro", "") for s in urgent_items[:3])
        extra = " y m\u00e1s..." if len(urgent_items) > 3 else ""
        sub_msg = f"<p style='color:#c0392b;font-size:0.85rem;margin-bottom:0.75rem;'>\U0001f534 <strong>{len(urgent_items)} urgente(s)</strong> — {nos_list}{extra} \u2014 \u00a1No has dado seguimiento! Por favor actualiza estos siniestros.</p>"
    elif warning_items:
        header_icon = "\u26a0\ufe0f"
        sub_msg = f"<p style='color:#b7950b;font-size:0.85rem;margin-bottom:0.75rem;'>\u26a0\ufe0f Tienes <strong>{len(warning_items)} siniestro(s)</strong> por vencer. No olvides actualizarlos antes de que se vuelvan urgentes.</p>"
    else:
        header_icon = "\U0001f514"
        sub_msg = f"<p style='color:#1a5276;font-size:0.85rem;margin-bottom:0.75rem;'>\U0001f514 Tienes <strong>{len(upcoming_items)} siniestro(s)</strong> que actualizar\u00e1n pronto. Mantente al d\u00eda.</p>"

    return f"""<div class="mazda-card pending-section">
  <h2>
    {header_icon} Pendientes de Seguimiento · Días hábiles
    <span class="pending-count">{total_pending}</span>
  </h2>
  {sub_msg}
  {items_html}
</div>"""


def get_global_alert_banner_html(red_count=0, yellow_count=0):
    """
    Generate a global alert banner shown at the top of the page
    when there are urgent/warning items. Returns empty string if none.
    """
    if red_count > 0:
        extra = " y " + str(yellow_count) + " por vencer" if yellow_count > 0 else ""
        return f"""<div class="global-alert-banner" id="globalAlertBanner">
  <span class="alert-icon">\U0001f6a8</span>
  <span class="alert-text">
    <strong>\u00a1ALERTA!</strong> Tienes <strong>{red_count} siniestro(s) urgente(s)</strong>{extra} — \u00a1No has dado seguimiento! <a href="/siniestros" style="color:#e31837;text-decoration:underline;">Ver todos</a>
  </span>
  <button class="alert-close" onclick="document.getElementById('globalAlertBanner').style.display='none'">&times;</button>
</div>"""
    elif yellow_count > 0:
        return f"""<div class="global-alert-banner warning" id="globalAlertBanner">
  <span class="alert-icon">\u26a0\ufe0f</span>
  <span class="alert-text">
    <strong>Recordatorio:</strong> Tienes <strong>{yellow_count} siniestro(s) por vencer</strong>. Actualiza antes de que sea urgente. <a href="/siniestros" style="color:#b7950b;text-decoration:underline;">Ver pendientes</a>
  </span>
  <button class="alert-close" onclick="document.getElementById('globalAlertBanner').style.display='none'">&times;</button>
</div>"""
    return ""


def get_toast_notification_js(red_count=0, yellow_count=0, total_pending=0):
    """
    Return JavaScript that shows toast notifications on page load
    if there are pending siniestros. Uses localStorage to avoid
    showing repeatedly on the same day.
    """
    if total_pending == 0:
        return ""

    today_str = "new Date().toISOString().split('T')[0]"

    # Build toast messages
    toasts = []
    if red_count > 0:
        s_s = "s" if red_count != 1 else ""
        msg = f"Tienes {red_count} siniestro{s_s} sin actualizar por m\\u00e1s de 12 d\\u00edas. \\u00a1Debes dar seguimiento ya!"
        toasts.append(f"{{type:'danger', icon:'\\ud83d\\udea8', title:'\\u00a1URGENTE!', message:'{msg}'}}")
    if yellow_count > 0:
        s_s = "s" if yellow_count != 1 else ""
        msg = f"{yellow_count} siniestro{s_s} est\\u00e1n por vencer (5-11 d\\u00edas sin actualizar). Actualiza pronto."
        toasts.append(f"{{type:'warning', icon:'\\u26a0\\ufe0f', title:'Pr\\u00f3ximo a vencer', message:'{msg}'}}")
    if red_count == 0 and yellow_count == 0 and total_pending > 0:
        msg = f"Tienes {total_pending} siniestro(s) para actualizar. No olvides dar seguimiento."
        toasts.append(f"{{type:'info', icon:'\\ud83d\\udd14', title:'Recordatorio', message:'{msg}'}}")

    toasts_json = "[" + ",".join(toasts) + "]"

    return f"""<div id="toastContainer" class="toast-container"></div>
<script>
(function() {{
    var today = {today_str};
    var lastShown = localStorage.getItem('toastLastShown');
    if (lastShown === today) return;

    var toasts = {toasts_json};

    function showToast(toast) {{
        var container = document.getElementById('toastContainer');
        var el = document.createElement('div');
        el.className = 'toast toast-' + toast.type;
        el.innerHTML =
            '<span class="toast-icon">' + toast.icon + '</span>' +
            '<div class="toast-body">' +
                '<div class="toast-title">' + toast.title + '</div>' +
                '<div class="toast-message">' + toast.message + '</div>' +
            '</div>' +
            '<button class="toast-close" onclick="this.parentElement.classList.add(\\'toast-out\\');setTimeout(function(){{this.parentElement.remove()}}.bind(this),300)">&times;</button>';
        container.appendChild(el);
        setTimeout(function() {{
            if (el.parentElement) {{
                el.classList.add('toast-out');
                setTimeout(function() {{ if (el.parentElement) el.remove(); }}, 300);
            }}
        }}, 8000);
    }}

    // Show each toast with a delay
    toasts.forEach(function(t, i) {{
        setTimeout(function() {{ showToast(t); }}, i * 1500 + 500);
    }});

    localStorage.setItem('toastLastShown', today);
    localStorage.setItem('toastLastCount', {total_pending});
}})();
</script>"""


def siniestro_row_html(sin):
    """Return a full <tr> for a siniestro record, with cost, status and action columns."""
    sc = sin.get("status_color", "green")

    terminado = sin.get("terminado", False)
    if terminado:
        sc = "terminados"

    row_class = f"row-{sc}"

    badge = status_badge_html(
        sc,
        sin.get("status_emoji", "\U0001f7e2"),
        sin.get("status_label", "Al d\u00eda"),
        sin.get("dias_desde_actualizacion", 0),
    )

    fecha = sin.get("fecha_actualizacion", "")
    tipo_cliente = sin.get("tipo_cliente", "particular")
    aseguradora = sin.get("aseguradora") or ("Particular" if tipo_cliente == "particular" else "Sin aseguradora")
    key = sin.get("nosiniestro", "")

    refacciones = sin.get("refacciones", 0)
    mano_obra = sin.get("mano_obra", 0)
    total = sin.get("total", 0)

    fmt_refacciones = f"${refacciones:,.2f}"
    fmt_mano_obra = f"${mano_obra:,.2f}"
    fmt_total = f"${total:,.2f}"

    if terminado:
        action_btn = f'<form method="post" action="/marcar-pendiente/{key}" style="display:inline"><button type="submit" class="btn btn-outline btn-sm">\U0001f504 Reabrir</button></form>'
    else:
        action_btn = f'<form method="post" action="/marcar-terminado/{key}" style="display:inline"><button type="submit" class="btn btn-success btn-sm">\u2705 Terminar</button></form>'

    return f"""<tr class="{row_class}">
  <td><strong>{key}</strong></td>
  <td><strong>{sin.get("orden", 0)}</strong></td>
  <td>{sin.get("modelo", "")}</td>
  <td>{sin.get("color", "")}</td>
  <td>{sin.get("placas", "")}</td>
  <td>{aseguradora}</td>
  <td>{fmt_refacciones}</td>
  <td>{fmt_mano_obra}</td>
  <td><strong>{fmt_total}</strong></td>
  <td><strong>{fecha}</strong><br><small style="color:#6b6b8a;">Último seguimiento</small></td>
  <td>{badge}</td>
  <td>{action_btn}</td>
</tr>"""

