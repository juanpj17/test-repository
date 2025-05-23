import os
import psutil
import subprocess
import time
from datetime import datetime
import openpyxl
from openpyxl import Workbook

# === CONFIGURACIÓN ===
repo_path = "repositorio-local"
remote_url = "https://github.com/juanpj17/test-repository.git"  # Reemplaza con tu repo con permisos de escritura
archivo_modificado = "archivo_test.txt"
excel_file = "modificacion_repo.xlsx"

def medir_consumo():
    return psutil.net_io_counters()

def guardar_en_excel(fecha, enviados, recibidos, duracion):
    total = enviados + recibidos

    if os.path.exists(excel_file):
        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Fecha", "Enviados (MB)", "Recibidos (MB)", "Total (MB)", "Duración (s)"])

    fila = [
        fecha.strftime("%Y-%m-%d %H:%M:%S"),
        round(enviados / (1024 * 1024), 2),
        round(recibidos / (1024 * 1024), 2),
        round(total / (1024 * 1024), 2),
        round(duracion, 2)
    ]
    ws.append(fila)
    wb.save(excel_file)

def inicializar_repo():
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)
        subprocess.run(["git", "init"], cwd=repo_path)
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=repo_path)

def simular_modificacion():
    ruta_archivo = os.path.join(repo_path, archivo_modificado)
    with open(ruta_archivo, "a", encoding="utf-8") as f:
        f.write(f"\nModificación en {datetime.now()}")

def realizar_commit_y_push():
    subprocess.run(["git", "add", "."], cwd=repo_path)
    subprocess.run(["git", "commit", "-m", "Modificación automática"], cwd=repo_path)
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_path)

# === FLUJO ===

inicializar_repo()
simular_modificacion()

print("Midiendo antes del push...")
inicio_red = medir_consumo()
inicio_tiempo = time.time()

realizar_commit_y_push()

fin_tiempo = time.time()
fin_red = medir_consumo()

enviados = fin_red.bytes_sent - inicio_red.bytes_sent
recibidos = fin_red.bytes_recv - inicio_red.bytes_recv
duracion = fin_tiempo - inicio_tiempo

print(f"\n📤 Enviados: {round(enviados / (1024 * 1024), 2)} MB")
print(f"📥 Recibidos: {round(recibidos / (1024 * 1024), 2)} MB")
print(f"⏱️ Duración: {round(duracion, 2)} segundos")

guardar_en_excel(datetime.now(), enviados, recibidos, duracion)
print(f"✅ Datos guardados en {excel_file}")
