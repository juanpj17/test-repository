import psutil
import subprocess
import time
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import os
import shutil
import stat

# === CONFIGURACIÓN ===
repo_url = "https://github.com/juanpj17/shopping-cart.git"  
excel_file = "consumo_github.xlsx"
repeticiones = 100
directorio_clonado = "shopping-cart"

# === FUNCIONES ===

def medir_consumo():
    return psutil.net_io_counters()

def guardar_en_excel(fecha, comando, enviados, recibidos, duracion):
    total = enviados + recibidos

    if os.path.exists(excel_file):
        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Fecha", "Comando", "Enviados (MB)", "Recibidos (MB)", "Total (MB)", "Duración (s)"])

    fila = [
        fecha.strftime("%Y-%m-%d %H:%M:%S"),
        " ".join(comando),
        round(enviados / (1024 * 1024), 2),
        round(recibidos / (1024 * 1024), 2),
        round(total / (1024 * 1024), 2),
        round(duracion, 2)
    ]
    ws.append(fila)
    wb.save(excel_file)


def eliminar_directorio_si_existe(path):
    if os.path.exists(path) and os.path.isdir(path):
        def onerror(func, path, exc_info):
            os.chmod(path, stat.S_IWRITE)  # Quitar solo lectura si aplica
            func(path)
        shutil.rmtree(path, onerror=onerror)

# === FLUJO PRINCIPAL ===
for i in range(1, repeticiones + 1):
    print(f"\n🔁 Repetición {i}/{repeticiones}")

    eliminar_directorio_si_existe(directorio_clonado) 

    git_command = ["git", "clone", repo_url]

    print("Midiendo uso de red antes de ejecutar el comando...")
    inicio_red = medir_consumo()
    inicio_tiempo = time.time()

    print(f"Ejecutando: {' '.join(git_command)}")
    subprocess.run(git_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  

    fin_tiempo = time.time()
    fin_red = medir_consumo()

    enviados = fin_red.bytes_sent - inicio_red.bytes_sent
    recibidos = fin_red.bytes_recv - inicio_red.bytes_recv
    duracion = fin_tiempo - inicio_tiempo

    print(f"📤 Enviados: {round(enviados / (1024 * 1024), 2)} MB")
    print(f"📥 Recibidos: {round(recibidos / (1024 * 1024), 2)} MB")
    print(f"⏱️ Duración: {round(duracion, 2)} segundos")

    guardar_en_excel(datetime.now(), git_command, enviados, recibidos, duracion)

    eliminar_directorio_si_existe(directorio_clonado)  
print("\n✅ Pruebas finalizadas. Datos guardados en", excel_file)