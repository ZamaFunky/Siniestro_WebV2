from datetime import datetime, date


ESTATUS_TALLER = [
 ("valuacion","Valuación"),("autorizacion","Autorización"),("reserva","Reserva"),
 ("esperando_piezas","Esperando piezas"),("citar","Citar"),("citado","Citado"),("colission","Colisión")
]

ASEGURADORAS = [
    ("AXA", "AXA"),
    ("GNP", "GNP"),
    ("Qualitas", "Qualitas"),
    ("HDI", "HDI"),
    ("Chubb", "Chubb"),
    ("Mapfre", "Mapfre"),
    ("Zurich", "Zurich"),
    ("ABA", "ABA"),
    ("Banorte", "Banorte"),
    ("Afirme", "Afirme"),
    ("Otra", "Otra")
]


def _tercer_lunes(year, month):
    """Tercer lunes del mes (festivo federal en México)."""
    d = date(year, month, 1)
    while d.weekday() != 0:
        d += __import__("datetime").timedelta(days=1)
    return d + __import__("datetime").timedelta(days=14)


def dias_inhabiles_mexico(year):
    """Festivos federales habituales en México usados por el tablero."""
    return {
        date(year, 1, 1),
        _tercer_lunes(year, 2),
        _tercer_lunes(year, 3),
        date(year, 5, 1),
        date(year, 9, 16),
        _tercer_lunes(year, 11),
        date(year, 12, 25),
    }


def es_dia_habil(d):
    return d.weekday() < 5 and d not in dias_inhabiles_mexico(d.year)


def contar_dias_habiles(inicio, fin=None):
    """Cuenta días hábiles transcurridos; no cuenta el día del seguimiento."""
    if not inicio:
        return 0
    if isinstance(inicio, str):
        try:
            inicio = datetime.strptime(inicio[:10], "%Y-%m-%d").date()
        except ValueError:
            return 0
    fin = fin or date.today()
    if fin <= inicio:
        return 0
    from datetime import timedelta
    total = 0
    actual = inicio
    while actual < fin:
        actual += timedelta(days=1)
        if actual <= fin and es_dia_habil(actual):
            total += 1
    return total

class Siniestro:
    def __init__(self, modelo=None,color=None,placas=None,nosiniestro=None,fecha_actualizacion=None, orden=0,
                 aseguradora=None,tipo_cliente="particular",terminado=False,refacciones=None,mano_obra=None,telefono=None,
                 estatus_taller=None,fecha_estatus_taller=None):
        self.modelo=modelo; self.color=color; self.placas=placas; self.nosiniestro=nosiniestro
        self.tipo_cliente = "aseguradora" if str(tipo_cliente or "particular").strip().lower() == "aseguradora" else "particular"
        self.aseguradora=aseguradora if self.tipo_cliente == "aseguradora" else None; self.orden=int(orden or 0); self.terminado=bool(terminado)
        self.refacciones=float(refacciones or 0); self.mano_obra=float(mano_obra or 0); self.telefono=telefono
        self.estatus_taller=estatus_taller or "valuacion"; self.fecha_estatus_taller=fecha_estatus_taller
        try: self.fecha_actualizacion=datetime.strptime(str(fecha_actualizacion),"%Y-%m-%d").date() if fecha_actualizacion else date.today()
        except: self.fecha_actualizacion=date.today()
    def get_modelo(self): return self.modelo
    def get_color(self): return self.color
    def get_placas(self): return self.placas
    def get_nosiniestro(self): return self.nosiniestro
    def get_aseguradora(self): return self.aseguradora
    def get_tipo_cliente(self): return self.tipo_cliente
    def get_tipo_cliente_label(self): return "Aseguradora" if self.tipo_cliente == "aseguradora" else "Particular"
    def get_terminado(self): return self.terminado
    def get_refacciones(self): return self.refacciones
    def get_mano_obra(self): return self.mano_obra
    def get_telefono(self): return self.telefono
    def get_estatus_taller(self): return self.estatus_taller
    def get_estatus_taller_label(self): return dict(ESTATUS_TALLER).get(self.estatus_taller,self.estatus_taller)
    def get_fecha_estatus_taller_str(self): return str(self.fecha_estatus_taller) if self.fecha_estatus_taller else None
    def get_dias_en_estatus_taller(self):
        if not self.fecha_estatus_taller: return 0
        try:
            return contar_dias_habiles(self.fecha_estatus_taller)
        except Exception:
            return 0
    def get_total(self): return round(self.refacciones+self.mano_obra,2)
    def get_fecha_str(self): return self.fecha_actualizacion.strftime("%Y-%m-%d")
    def get_dias_desde_actualizacion(self): return contar_dias_habiles(self.fecha_actualizacion)
    def get_status_color(self):
        d=self.get_dias_desde_actualizacion()
        return "green" if d<=4 else ("yellow" if d<=11 else "red")
    def get_status_emoji(self):
        return {"green":"🟢","yellow":"🟡","red":"🔴"}[self.get_status_color()]
    def get_status_label(self):
        return {"green":"Al día","yellow":"Por vencer","red":"Urgente"}[self.get_status_color()]
    def ValidarSiniestro(self):
        basicos = all(str(x).strip() for x in [self.modelo,self.color,self.placas,self.nosiniestro])
        if not basicos:
            return False
        if self.tipo_cliente == "aseguradora" and not self.aseguradora:
            return False
        return True
