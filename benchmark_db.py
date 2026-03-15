import lancedb
import numpy as np
import time
import shutil
import os

DB_PATH = "./test_stress_db"
if os.path.exists(DB_PATH): shutil.rmtree(DB_PATH)

db = lancedb.connect(DB_PATH)
DIM = 1024
BATCH_SIZE = 10000
TOTAL_RECORDS = 50000

print(f"--- INICIANDO LANCEDB STRESS TEST ({TOTAL_RECORDS} Vectores) ---")

# 1. Generar datos sintéticos
t0 = time.time()
data = [{"id": i, "vector": np.random.rand(DIM).astype(np.float32), "text": f"dummy_{i}"} for i in range(TOTAL_RECORDS)]
print(f"Generación de datos en RAM: {time.time() - t0:.2f}s")

# 2. Prueba de Escritura (I/O Máximo)
t1 = time.time()
tbl = db.create_table("stress_table", data=data)
t_write = time.time() - t1
print(f"ESCRITURA: {t_write:.2f}s ({TOTAL_RECORDS / t_write:.0f} filas/segundo)")

# 3. Prueba de Búsqueda (Lectura/Indexación)
query_vector = np.random.rand(DIM).astype(np.float32)
t2 = time.time()
results = tbl.search(query_vector).limit(10).to_pandas()
t_search = (time.time() - t2) * 1000
print(f"BÚSQUEDA (Top 10 en {TOTAL_RECORDS}): {t_search:.2f} ms")

# Limpieza
shutil.rmtree(DB_PATH)
print("--- TEST FINALIZADO ---")
