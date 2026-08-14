import os
from datetime import date
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3307")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Petra09"),
    "database": os.getenv("MYSQL_DATABASE", "siniestro_web_v2"),
    "charset": "utf8mb4",
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def ensure_schema():
    """Compatibilidad automática con BD creadas con versiones anteriores.
    No borra datos: solamente agrega las columnas que el sistema necesita.
    """
    c = get_conn()
    cur = c.cursor(dictionary=True)
    try:
        cur.execute("SHOW COLUMNS FROM siniestros")
        cols = {row["Field"] for row in cur.fetchall()}

        if "orden" not in cols:
            cur.execute("ALTER TABLE siniestros ADD COLUMN orden INT NOT NULL DEFAULT 0 AFTER nosiniestro")

        if "tipo_cliente" not in cols:
            cur.execute("ALTER TABLE siniestros ADD COLUMN tipo_cliente ENUM('particular','aseguradora') NOT NULL DEFAULT 'particular' AFTER nosiniestro")

        # Los registros que ya tenían aseguradora se consideran de tipo aseguradora.
        cur.execute("UPDATE siniestros SET tipo_cliente=CASE WHEN id_aseguradora IS NULL THEN 'particular' ELSE 'aseguradora' END")

        if "estatus_taller" not in cols:
            cur.execute("""ALTER TABLE siniestros ADD COLUMN estatus_taller ENUM(
                'valuacion','autorizacion','reserva','esperando_piezas',
                'citar','citado','colission'
            ) NOT NULL DEFAULT 'valuacion' AFTER telefono""")

        if "fecha_estatus_taller" not in cols:
            cur.execute("ALTER TABLE siniestros ADD COLUMN fecha_estatus_taller DATE NULL AFTER estatus_taller")
            cur.execute("UPDATE siniestros SET fecha_estatus_taller=COALESCE(fecha_actualizacion,CURDATE()) WHERE fecha_estatus_taller IS NULL")

        c.commit()
    finally:
        cur.close()
        c.close()


def ensure_connection():
    try:
        c=get_conn(); c.close(); return True
    except Error as e:
        print("MySQL:", e); return False

def _aseg_id(cur, nombre):
    if not nombre: return None
    cur.execute("SELECT id_aseguradora FROM aseguradoras WHERE nombre=%s", (nombre,))
    r=cur.fetchone()
    if r: return r[0]
    cur.execute("INSERT INTO aseguradoras(nombre) VALUES(%s)", (nombre,))
    return cur.lastrowid

def row_to_dict(r):
    if not r:
        return None
    from clases.Siniestro import Siniestro
    sin = Siniestro(
        modelo=r.get("modelo"),
        color=r.get("color"),
        placas=r.get("placas"),
        nosiniestro=r.get("nosiniestro"),
        fecha_actualizacion=r.get("fecha_actualizacion"),
        orden=r.get("orden") or 0,
        tipo_cliente=r.get("tipo_cliente") or ("aseguradora" if r.get("aseguradora") else "particular"),
        aseguradora=r.get("aseguradora"),
        terminado=bool(r.get("terminado")),
        refacciones=r.get("refacciones") or 0,
        mano_obra=r.get("mano_obra") or 0,
        telefono=r.get("telefono"),
        estatus_taller=r.get("estatus_taller") or "valuacion",
        fecha_estatus_taller=r.get("fecha_estatus_taller"),
    )
    return {
        "id_siniestro": r.get("id_siniestro"),
        "modelo": sin.get_modelo(),
        "color": sin.get_color(),
        "placas": sin.get_placas(),
        "nosiniestro": sin.get_nosiniestro(),
        "aseguradora": sin.get_aseguradora(),
        "terminado": sin.get_terminado(),
        "refacciones": sin.get_refacciones(),
        "mano_obra": sin.get_mano_obra(),
        "telefono": sin.get_telefono(),
        "orden": sin.orden,
        "tipo_cliente": sin.get_tipo_cliente(),
        "tipo_cliente_label": sin.get_tipo_cliente_label(),
        "estatus_taller": sin.get_estatus_taller(),
        "estatus_taller_label": sin.get_estatus_taller_label(),
        "fecha_estatus_taller": sin.get_fecha_estatus_taller_str(),
        "dias_en_estatus_taller": sin.get_dias_en_estatus_taller(),
        "fecha_actualizacion": sin.get_fecha_str(),
        "dias_desde_actualizacion": sin.get_dias_desde_actualizacion(),
        "dias_habiles": sin.get_dias_desde_actualizacion(),
        "total": sin.get_total(),
        "status_color": "terminados" if sin.get_terminado() else sin.get_status_color(),
        "status_emoji": "🔵" if sin.get_terminado() else sin.get_status_emoji(),
        "status_label": "Terminado" if sin.get_terminado() else sin.get_status_label(),
    }

def get_aseguradoras():
    """Obtiene las aseguradoras activas directamente desde MySQL."""
    ensure_schema()
    c = get_conn(); cur = c.cursor(dictionary=True)
    try:
        cur.execute("SELECT id_aseguradora, nombre FROM aseguradoras WHERE activo=TRUE ORDER BY nombre ASC")
        return cur.fetchall()
    finally:
        cur.close(); c.close()


def fetch_all():
    ensure_schema()
    c=get_conn(); cur=c.cursor(dictionary=True)
    cur.execute("""SELECT s.*, a.nombre AS aseguradora
                   FROM siniestros s LEFT JOIN aseguradoras a ON s.id_aseguradora=a.id_aseguradora
                   ORDER BY s.orden ASC, s.id_siniestro ASC""")
    rows=[row_to_dict(x) for x in cur.fetchall()]
    cur.close(); c.close()
    return rows

def fetch_one(key):
    ensure_schema()
    c=get_conn(); cur=c.cursor(dictionary=True)
    cur.execute("""SELECT s.*, a.nombre AS aseguradora
                   FROM siniestros s LEFT JOIN aseguradoras a ON s.id_aseguradora=a.id_aseguradora
                   WHERE s.nosiniestro=%s""",(key,))
    r=row_to_dict(cur.fetchone()); cur.close(); c.close(); return r

def insert_siniestro(d):
    ensure_schema()
    c=get_conn(); cur=c.cursor()
    tipo = "aseguradora" if str(d.get("tipo_cliente") or "particular").strip().lower() == "aseguradora" else "particular"
    aid=_aseg_id(cur,d.get("aseguradora")) if tipo == "aseguradora" else None
    if tipo == "aseguradora" and not d.get("aseguradora"):
        raise ValueError("La aseguradora es obligatoria cuando el tipo de cliente es aseguradora")
    no = str(d.get("nosiniestro") or "").strip().upper()
    etapa = d.get("fecha_estatus_taller") or date.today().strftime("%Y-%m-%d")
    cur.execute("""INSERT INTO siniestros
      (nosiniestro,orden,tipo_cliente,modelo,color,placas,fecha_actualizacion,id_aseguradora,refacciones,mano_obra,telefono,estatus_taller,fecha_estatus_taller,terminado)
      VALUES(%s,%s,%s,%s,%s,%s,COALESCE(%s,CURDATE()),%s,%s,%s,%s,%s,%s,%s)""",
      (no,d.get("orden") or 0,tipo,d["modelo"],d["color"],d["placas"],d.get("fecha_actualizacion"),aid,
       d.get("refacciones") or 0,d.get("mano_obra") or 0,d.get("telefono"),
       d.get("estatus_taller") or "valuacion",etapa,1 if d.get("terminado") else 0))
    c.commit(); cur.close(); c.close()
    return fetch_one(no)

def update_siniestro(key, d):
    """Actualiza únicamente los campos recibidos.
    Si cambia el estatus del taller, reinicia su contador.
    """
    ensure_schema()
    c = get_conn(); cur = c.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM siniestros WHERE nosiniestro=%s", (key,))
        actual = cur.fetchone()
        if not actual:
            return None

        fields = []
        vals = []
        allowed = {
            "orden", "tipo_cliente", "modelo", "color", "placas", "id_aseguradora",
            "refacciones", "mano_obra", "telefono", "fecha_actualizacion",
            "terminado", "estatus_taller", "fecha_estatus_taller"
        }

        # Tipo de cliente controla si se guarda aseguradora o particular.
        tipo_nuevo = str(d.get("tipo_cliente") or actual.get("tipo_cliente") or ("aseguradora" if actual.get("id_aseguradora") else "particular")).strip().lower()
        if tipo_nuevo not in {"particular", "aseguradora"}:
            tipo_nuevo = "particular"
        fields.append("tipo_cliente=%s"); vals.append(tipo_nuevo)

        # Si llega aseguradora por nombre, convertirla a id antes de actualizar.
        if "tipo_cliente" in d or "aseguradora" in d:
            nombre = d.get("aseguradora") if tipo_nuevo == "aseguradora" else None
            aid = None
            if tipo_nuevo == "aseguradora" and not nombre:
                raise ValueError("La aseguradora es obligatoria cuando el tipo de cliente es aseguradora")
            if nombre:
                cur.execute("SELECT id_aseguradora FROM aseguradoras WHERE nombre=%s", (nombre,))
                rr = cur.fetchone()
                if rr:
                    aid = rr["id_aseguradora"]
                else:
                    cur.execute("INSERT INTO aseguradoras(nombre) VALUES(%s)", (nombre,))
                    aid = cur.lastrowid
            fields.append("id_aseguradora=%s"); vals.append(aid)

        mapping = {
            "orden": "orden", "modelo": "modelo", "color": "color", "placas": "placas",
            "refacciones": "refacciones", "mano_obra": "mano_obra", "telefono": "telefono",
            "fecha_actualizacion": "fecha_actualizacion", "terminado": "terminado"
        }
        for key_name, column in mapping.items():
            if key_name in d:
                value = d.get(key_name)
                if key_name == "orden":
                    try: value = int(value or 0)
                    except (TypeError, ValueError): value = 0
                if key_name in {"refacciones", "mano_obra"}:
                    try: value = float(value or 0)
                    except (TypeError, ValueError): value = 0
                if key_name == "terminado":
                    value = 1 if value else 0
                fields.append(f"{column}=%s"); vals.append(value)

        if "estatus_taller" in d:
            nuevo = str(d.get("estatus_taller") or "valuacion").strip()
            anterior = actual.get("estatus_taller") or "valuacion"
            fields.append("estatus_taller=%s"); vals.append(nuevo)
            # Solo reinicia el contador si realmente cambió la etapa.
            if nuevo != anterior:
                fields.append("fecha_estatus_taller=%s")
                vals.append(d.get("fecha_estatus_taller") or date.today().strftime("%Y-%m-%d"))
            elif "fecha_estatus_taller" in d and d.get("fecha_estatus_taller"):
                fields.append("fecha_estatus_taller=%s"); vals.append(d.get("fecha_estatus_taller"))
        elif "fecha_estatus_taller" in d:
            fields.append("fecha_estatus_taller=%s"); vals.append(d.get("fecha_estatus_taller"))

        if not fields:
            return fetch_one(key)

        cur.execute("UPDATE siniestros SET " + ",".join(fields) + " WHERE nosiniestro=%s", vals + [key])
        c.commit()
    finally:
        cur.close(); c.close()
    return fetch_one(key)

def delete_siniestro(key):
    c=get_conn(); cur=c.cursor()
    cur.execute("DELETE FROM siniestros WHERE nosiniestro=%s",(key,))
    ok=cur.rowcount>0; c.commit(); cur.close(); c.close(); return ok

def add_comment(key, text):
    c=get_conn(); cur=c.cursor()
    cur.execute("SELECT id_siniestro FROM siniestros WHERE nosiniestro=%s",(key,))
    r=cur.fetchone()
    if not r: cur.close(); c.close(); return None
    cur.execute("INSERT INTO comentarios(id_siniestro,comentario) VALUES(%s,%s)",(r[0],text))
    cid=cur.lastrowid; c.commit(); cur.close(); c.close(); return cid

def comments(key):
    c=get_conn(); cur=c.cursor(dictionary=True)
    cur.execute("""SELECT c.id_comentario,c.id_siniestro,c.comentario,c.fecha_comentario
                   FROM comentarios c JOIN siniestros s ON c.id_siniestro=s.id_siniestro
                   WHERE s.nosiniestro=%s ORDER BY c.fecha_comentario DESC""",(key,))
    r=cur.fetchall(); cur.close(); c.close()
    return r
