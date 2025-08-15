from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from materiales import PARAMETROS_LADRILLOS, MATERIALES_ADICIONALES
from mercadolibre import buscar_precio
from typing import Dict

app = FastAPI(
    title="API de Cálculo de Construcción",
    description="Calcula materiales y costos para paredes con precios de MercadoLibre.",
)

class MaterialResponse(BaseModel):
    tipo_ladrillo: str
    metros_cuadrados: float
    materiales: Dict[str, float]
    costos_estimados: Dict[str, float]
    costo_total: float

@app.get("/calcular/", response_model=MaterialResponse)
async def calcular_pared(
    tipo: str = Query(..., description="Tipo de ladrillo: comun, hueco, bloque"),
    metros: float = Query(..., gt=0, description="Metros cuadrados de la pared"),
):
    if tipo not in PARAMETROS_LADRILLOS:
        raise HTTPException(status_code=400, detail="Tipo de ladrillo no válido.")
    
    # Calcular materiales
    datos = PARAMETROS_LADRILLOS[tipo]
    materiales = {
        "ladrillos": round(metros * datos["cantidad_por_m2"]),
        "arena_m3": round(metros * datos["arena_m3"], 2),
        "cemento_kg": round(metros * datos["cemento_kg"], 1),
        **{k: round(metros * v, 2) for k, v in MATERIALES_ADICIONALES.items()},
    }

    # Obtener precios
    precios = {
        "ladrillos": buscar_precio(f"ladrillo {datos['nombre']}"),
        "arena_m3": buscar_precio("arena m3 construcción"),
        "cemento_kg": buscar_precio("cemento 50 kg") / 50,
        "cal_kg": buscar_precio("cal kg construcción"),
        **{k: buscar_precio(k.replace("_", " ")) for k in MATERIALES_ADICIONALES},
    }

    # Calcular costos
    costos = {k: round(v * precios[k], 2) for k, v in materiales.items()}
    total = sum(costos.values())

    return {
        "tipo_ladrillo": datos["nombre"],
        "metros_cuadrados": metros,
        "materiales": materiales,
        "costos_estimados": costos,
        "costo_total": total,
    }

@app.get("/")
async def home():
    return {"Instrucciones": "Use /calcular/?tipo=comun&metros=10"}