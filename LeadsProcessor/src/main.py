import os
import csv
from datetime import datetime
from src.db.connection import get_connection
from src.utils.file_utils import get_csv_files, move_to_processed
from src.utils.validators import is_valid_phone, is_valid_name, is_valid_dob
from src.utils.logger import setup_logger

INPUT_DIR = "LeadsProcessor/data/LEADS_PROCESAR"
PROCESSED_DIR = "LeadsProcessor/data/PROCESADOS"
LOG_FILE = "LeadsProcessor/output/logs/proceso.log"
REPORT_FILE = "LeadsProcessor/output/reportes/resumen.csv"

logger = setup_logger("leads_processor", LOG_FILE)

def process_csv(file_path):
    total, insertados, rechazados = 0, 0, 0
    conn = get_connection()
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total += 1
            try:
                phone = row["PHONE"]
                if not (is_valid_name(row["FN"]) and is_valid_name(row["LN"])):
                    raise ValueError("Nombre inválido")
                if not is_valid_phone(phone):
                    raise ValueError("Teléfono inválido")
                if not is_valid_dob(row["DOB_MON"], row["DOB_DAY"], row["DOB_YEAR"]):
                    raise ValueError("Fecha de nacimiento inválida")

                birthday = f"{int(row['DOB_YEAR']):04d}-{int(row['DOB_MON']):02d}-{int(row['DOB_DAY']):02d}"

                cursor.execute(
                    '''INSERT INTO leads (first_name, last_name, phone, address, city, state, zip_code, birthday, is_dnc, v_dnc)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (first_name, last_name, phone) DO NOTHING''',
                    (row["FN"], row["LN"], phone, row["ADDR"], row["CITY"], row["ST"], row["ZIP"], birthday,
                     row.get("IS_DNC", "0"), row.get("V_DNC", "0"))
                )
                if cursor.rowcount:
                    insertados += 1
                else:
                    rechazados += 1

            except Exception as e:
                logger.error(f"❌ Error en línea {total}: {e}")
                rechazados += 1

    conn.commit()
    cursor.close()
    conn.close()
    return total, insertados, rechazados

def generar_reporte(nombre_archivo, total, insertados, rechazados):
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    encabezado = not os.path.exists(REPORT_FILE)
    with open(REPORT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if encabezado:
            writer.writerow(["Archivo", "Fecha", "Total", "Insertados", "Rechazados"])
        writer.writerow([nombre_archivo, datetime.now().isoformat(), total, insertados, rechazados])

def main():
    archivos = get_csv_files(INPUT_DIR)
    if not archivos:
        print("📂 No hay archivos para procesar.")
        return

    for archivo in archivos:
        print(f"📥 Procesando: {archivo.name}")
        total, insertados, rechazados = process_csv(archivo)
        generar_reporte(archivo.name, total, insertados, rechazados)
        move_to_processed(archivo, PROCESSED_DIR)
        print(f"✅ Completado: {archivo.name} — Insertados: {insertados}, Rechazados: {rechazados}")

if __name__ == "__main__":
    main()
