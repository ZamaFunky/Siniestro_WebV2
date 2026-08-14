from db import fetch_all, fetch_one, insert_siniestro, update_siniestro, delete_siniestro

class Row(dict):
    def __init__(self, data, store):
        super().__init__(data); self._store=store

    def __setitem__(self, k, v):
        if k == "nosiniestro":
            super().__setitem__(k, v)
            return
        super().__setitem__(k, v)
        if k in {
            "orden","tipo_cliente","modelo","color","placas","aseguradora","refacciones",
            "mano_obra","telefono","terminado","estatus_taller","fecha_estatus_taller",
            "fecha_actualizacion"
        }:
            update_siniestro(self.get("nosiniestro"), {k: v})

class DBStore:
    def __len__(self): return len(fetch_all())
    def __contains__(self,key): return fetch_one(str(key)) is not None
    def __getitem__(self,key):
        r=fetch_one(str(key))
        if r is None: raise KeyError(key)
        return Row(r,self)
    def get(self,key,default=None):
        r=fetch_one(str(key)); return Row(r,self) if r else default
    def values(self):
        return [Row(x,self) for x in fetch_all()]
    def items(self):
        return [(x["nosiniestro"],Row(x,self)) for x in fetch_all()]
    def __setitem__(self,key,value):
        d=dict(value); d["nosiniestro"]=str(key)
        if fetch_one(str(key)): update_siniestro(str(key),d)
        else: insert_siniestro(d)
    def pop(self,key,default=None):
        old=fetch_one(str(key))
        if old is None:
            if default is not None: return default
            raise KeyError(key)
        delete_siniestro(str(key)); return old
