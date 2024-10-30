import pandas as pd
import ijson

# Archivo JSON de entrada y archivo Excel de salida
nombre_archivo_json = "./Json/sell_out_final.json"
nombre_archivo_excel = "sell_out_final_output.xlsx"

# Usar ijson para cargar datos JSON grandes en un DataFrame
datos = []
with open(nombre_archivo_json, "r", encoding="utf-8") as archivo_json:
    # Lee los datos en forma de flujo usando ijson
    for objeto in ijson.items(archivo_json, "item"):
        datos.append(objeto)

# Crear un DataFrame con los datos cargados
df = pd.DataFrame(datos)

# Guardar el DataFrame en un archivo Excel
df.to_excel(nombre_archivo_excel, index=False, engine="openpyxl")

print(f"Archivo '{nombre_archivo_excel}' generado exitosamente.")
