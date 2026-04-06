from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="API Gimnasio")

app.add_middleware(
    CORSMiddleware,
    origins = [
    "https://fancy-griffin-42f3aa.netlify.app", # ¡Tu página en producción!
    "http://localhost:5500", # Útil por si estás probando tu HTML localmente en tu compu
    "http://127.0.0.1:5500"
]

# 2. Le agregas el filtro de seguridad (CORS) a tu app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # El "*" significa que permites POST, GET, PUT, DELETE, etc.
    allow_headers=["*"], # Permite enviar cualquier tipo de dato (como JSON)
)
)

# ⚠️ PEGA AQUÍ TU CONNECTION STRING DE SUPABASE (Empieza con postgresql://)
DATABASE_URL = "postgresql://postgres:Locuracamila02*@db.cjqyzrfrjqtaikswdqim.supabase.co:5432/postgres"

def obtener_conexion():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# --- MODELOS DE DATOS ---
class NuevoEjercicio(BaseModel):
    nombre: str
    grupo_muscular: str

class NuevaSesion(BaseModel):
    notas: str = ""

class NuevoRegistro(BaseModel):
    id_sesion: int
    id_ejercicio: int
    numero_serie: int
    repcell_reps: int
    peso_kg: float

class NuevaMetrica(BaseModel):
    peso_kg: float
    medida_abdomen_cm: float
    notas: str = ""

# --- RUTAS ---
@app.get("/ejercicios")
def obtener_ejercicios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM Ejercicios')
    resultado = cursor.fetchall()
    conexion.close()
    return {"ejercicios": resultado}

@app.post("/ejercicios")
def agregar_ejercicio(ejercicio: NuevoEjercicio):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO Ejercicios (nombre, grupo_muscular) VALUES (%s, %s)", 
                   (ejercicio.nombre, ejercicio.grupo_muscular))
    conexion.commit()
    conexion.close()
    return {"mensaje": f"Ejercicio '{ejercicio.nombre}' añadido correctamente"}

@app.post("/sesiones")
def crear_sesion(sesion: NuevaSesion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO Sesiones (notas) VALUES (%s) RETURNING id", (sesion.notas,))
    nuevo_id = cursor.fetchone()['id']
    conexion.commit()
    conexion.close()
    return {"id_sesion": nuevo_id}

@app.post("/registros")
def agregar_registro(registro: NuevoRegistro):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO Registros_Rutina 
        (id_sesion, id_ejercicio, numero_serie, repeticiones, peso_kg) 
        VALUES (%s, %s, %s, %s, %s)
    """, (registro.id_sesion, registro.id_ejercicio, registro.numero_serie, registro.repcell_reps, registro.peso_kg))
    conexion.commit()
    conexion.close()
    return {"mensaje": "Serie registrada"}

@app.post("/metricas")
def registrar_metrica(metrica: NuevaMetrica):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO Metricas_Corporales (peso_kg, medida_abdomen_cm, notas) 
        VALUES (%s, %s, %s)
    """, (metrica.peso_kg, metrica.medida_abdomen_cm, metrica.notas))
    conexion.commit()
    conexion.close()
    return {"mensaje": "Métrica corporal guardada"}

@app.get("/metricas")
def obtener_metricas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM Metricas_Corporales ORDER BY fecha ASC')
    resultado = cursor.fetchall()
    conexion.close()
    return {"historial": resultado}
