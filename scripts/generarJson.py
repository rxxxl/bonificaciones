import pandas as pd
from pathlib import Path
import json
import os

# Ruta del archivo Excel
archivo_clientes = Path('.\\data\\Calculo Carnot.xlsx')
archivo_negociacion = Path('.\\data\\enf.xlsx')
# Crear la carpeta 'data' si no existe
carpeta_data = './Json'
os.makedirs(carpeta_data, exist_ok=True)

# Función para generar JSON de Clientes Aplicables
def generar_json_clientes(archivo_excel):
    try:
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo_excel)
        
        # Obtener los nombres de todas las hojas
        hojas = xls.sheet_names
        print(f"Hojas encontradas en el archivo de clientes: {hojas}")  # Para depuración

        for hoja in hojas:

            if hoja.lower() == 'ofertas':
                print(f"Omitiendo la hoja '{hoja}'.")
                continue  # Salta a la siguiente iteración del bucle

            # Leer cada hoja
            df = pd.read_excel(xls, sheet_name=hoja)

            # Eliminar columnas que no tienen nombre o están vacías
            df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]

            # Convertir el Sivec a string si es necesario (opcional)
            if 'Sivec' in df.columns:
                df['Sivec'] = df['Sivec'].astype(str)
                
            #Convertir correctamente la columna Fecha
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.strftime('%m/%d/%Y')
                

            # Crear el nuevo campo 'Llave'
            if 'RETAIL' in df.columns:
                df['Llave'] = df['RETAIL'].astype(str) + df['Sivec']
            else:
                print(f"La columna 'RETAIL' no se encontró en la hoja '{hoja}'.")

            # Convertir el DataFrame a JSON
            json_data = df.to_json(orient='records', force_ascii=False)

            # Sustituir espacios por guiones bajos en el nombre de la hoja
            nombre_json = f"{hoja.replace(' ', '_')}.json"
            ruta_json = os.path.join(carpeta_data, nombre_json)

            # Guardar el JSON en el archivo especificado
            with open(ruta_json, 'w', encoding='utf-8') as json_file:
                json.dump(json.loads(json_data), json_file, ensure_ascii=False, indent=4)

            print(f"Conversión a JSON completada para la hoja '{hoja}'. Los datos se han guardado en '{ruta_json}'.")

    except Exception as e:
        print(f"Se produjo un error al procesar el archivo de clientes: {e}")

# Función para generar JSON de Negociaciones
def generar_json_negociacion(archivo_excel):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_excel)

        # Convertir fechas a un formato más legible (si es necesario)
        df['Fecha inicio vigencia'] = pd.to_datetime(df['Fecha inicio vigencia'], errors='coerce').dt.strftime('%m/%d/%Y')
        df['Fecha fin vigencia'] = pd.to_datetime(df['Fecha fin vigencia'], errors='coerce').dt.strftime('%m/%d/%Y')

        # Crear el nuevo campo 'Llave' concatenando 'Nombre alias' y 'Sivec'
        df['Llave'] = df['Nombre alias'].astype(str) + df['Sivec'].astype(str)

        # Eliminar columnas sin nombre
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]

        # Convertir el DataFrame a JSON
        json_data = df.to_json(orient='records', force_ascii=False)

        # Guardar el JSON en un archivo con nombre específico
        ruta_json_negociacion = os.path.join(carpeta_data, 'negociacion.json')
        with open(ruta_json_negociacion, 'w', encoding='utf-8') as json_file:
            json.dump(json.loads(json_data), json_file, ensure_ascii=False, indent=4)

        print("Conversión a JSON de negociaciones completada. Los datos se han guardado en 'negociacion.json'.")

    except Exception as e:
        print(f"Se produjo un error al procesar el archivo de negociación: {e}")

# Función para generar JSON de Ofertas
def generar_json_ofertas(ruta_negociacion):
    ruta_oferta_sell_out = os.path.join(carpeta_data, 'ofertaSellOut.json')
    ruta_oferta_sell_in = os.path.join(carpeta_data, 'ofertaSellIn.json')
    ruta_oferta_final = os.path.join(carpeta_data, 'ofertaFinal.json')  # Archivo combinado

    try:
        # Validar si el archivo de negociaciones existe
        if not os.path.isfile(ruta_negociacion):
            print(f'Error: El archivo {ruta_negociacion} no existe.')
            return

        # Cargar datos del archivo negociacion.json
        with open(ruta_negociacion, 'r', encoding='utf-8') as file:
            datos_negociacion = json.load(file)

        # Diccionarios para almacenar los datos por 'Llave' y por tipo de condición
        datos_por_llave_sell_out = {}
        datos_por_llave_sell_in = {}

        # Procesar cada registro en datos_negociacion
        for registro in datos_negociacion:
            llave = registro.get('Llave', 'N/A')
            folio_caso = registro.get('Folio caso', None)
            tipo_condicion = registro.get('Tipo condicion', 'N/A')

            # Elegir el diccionario correcto basado en el tipo de condición
            if tipo_condicion == 'SELL-OUT':
                datos_por_llave = datos_por_llave_sell_out
            elif tipo_condicion == 'SELL-IN':
                datos_por_llave = datos_por_llave_sell_in
            else:
                # Si no es ni SELL-OUT ni SELL-IN, ignorar este registro
                continue
                
            def obtener_nivel(datos):
                if datos.get('Nombre alias'):
                    return 'Nombre alias'
                elif datos.get('Nombre segmento'):
                    return 'Nombre segmento'
                elif datos.get('Nombre subsegmento'):
                    return 'Nombre subsegmento'
                elif datos.get('Numero Cliente'):
                    return 'Numero Cliente'
                elif datos.get('Nombre cliente'):
                    return 'Nombre cliente'
                return 'N/A'  # En caso de que ninguno tenga valor


            # Inicializar estructura para almacenar CAP y OFERTA si no existe para esta llave
            if llave not in datos_por_llave:
                datos_por_llave[llave] = {
                    'Nombre alias': registro.get('Nombre alias', 'N/A'),
                    'Sivec': registro.get('Sivec', 'N/A'),
                    'NOMBRE': registro.get('Nombre articulo', 'N/A'),
                    'CAP': 0.0,
                    'OFERTA': 0.0,
                    'Nombre regla': registro.get('Nombre regla', 'N/A'),
                    'Costo fijo': registro.get('Costo fijo', 0.0),
                    'Nivel': obtener_nivel(registro),
                    'Nombre segmento': registro.get('Nombre segmento', 'N/A'),
                    'Nombre subsegmento': registro.get('Nombre subsegmento', 'N/A'),
                    'Numero Cliente': registro.get('Numero Cliente', 'N/A'),
                    'Nombre cliente': registro.get('Nombre cliente', 'N/A'),
                    'Tipo condicion costo': registro.get('Tipo condicion costo', 'N/A'),
                    'Fecha inicio vigencia': registro.get('Fecha inicio vigencia', 'N/A'),
                    'Fecha fin vigencia': registro.get('Fecha fin vigencia', 'N/A'),
                    'Tipo condicion': tipo_condicion  # Agregar campo "Tipo condicion"
                }

            # Asignar CAP cuando el folio de caso es 1, y OFERTA cuando es 2
            if folio_caso == 1:
                datos_por_llave[llave]['CAP'] = registro.get('Oferta costo', 0.0)
            elif folio_caso == 2:
                datos_por_llave[llave]['OFERTA'] = registro.get('Oferta costo', 0.0)

        # Función para generar registros finales con ponderado
        def generar_registros_finales(datos_por_llave):
            registros_finales = []
            for llave, datos in datos_por_llave.items():
                cap = datos['CAP']
                oferta = datos['OFERTA']
                ponderado = 1 - (1 - cap) * (1 - oferta)
                datos['PONDERADO'] = ponderado

                # Reordenar campos, asegurando que 'Llave' esté al final
                registro_ordenado = {
                    'Nombre regla': datos['Nombre regla'],
                    'Costo fijo': datos['Costo fijo'],
                    "Tipo condicion costo": datos['Tipo condicion costo'],
                    'CAP': datos['CAP'],
                    'Oferta': datos['OFERTA'],
                    'Nivel': datos['Nivel'],
                    'Nombre segmento': datos['Nombre segmento'],
                    'Nombre subsegmento': datos['Nombre subsegmento'],
                    'Nombre alias': datos['Nombre alias'],
                    'Numero Cliente': datos['Numero Cliente'],
                    'Nombre cliente': datos['Nombre cliente'],
                    'Nombre': datos['NOMBRE'],
                    'Ponderado': datos['PONDERADO'],
                    'Fecha inicio vigencia': datos['Fecha inicio vigencia'],
                    'Fecha fin vigencia': datos['Fecha fin vigencia'],
                    'Sivec': datos['Sivec'],
                    'Tipo condicion': datos['Tipo condicion'],  # Mantener el campo "Tipo condicion"
                    'Llave': llave
                }
                registros_finales.append(registro_ordenado)
            return registros_finales

        # Generar los registros finales para SELL-OUT y SELL-IN
        registros_sell_out = generar_registros_finales(datos_por_llave_sell_out)
        registros_sell_in = generar_registros_finales(datos_por_llave_sell_in)

        # Crear el archivo combinado con todos los registros (SELL-OUT y SELL-IN)
        registros_finales_combinados = registros_sell_out + registros_sell_in

        # Guardar los datos transformados en ofertaSellOut.json, ofertaSellIn.json y ofertaFinal.json
        with open(ruta_oferta_sell_out, 'w', encoding='utf-8') as file:
            json.dump(registros_sell_out, file, ensure_ascii=False, indent=4)

        with open(ruta_oferta_sell_in, 'w', encoding='utf-8') as file:
            json.dump(registros_sell_in, file, ensure_ascii=False, indent=4)

        with open(ruta_oferta_final, 'w', encoding='utf-8') as file:
            json.dump(registros_finales_combinados, file, ensure_ascii=False, indent=4)

        print(f'Transformación completada. Archivos guardados en {ruta_oferta_sell_out}, {ruta_oferta_sell_in} y {ruta_oferta_final}.')

    except FileNotFoundError:
        print(f'Error: No se encontró el archivo {ruta_negociacion}.')
    except json.JSONDecodeError:
        print('Error: El archivo JSON está mal formado.')
    except Exception as e:
        print(f'Se produjo un error inesperado: {e}')
# Ejecutar las funciones
generar_json_clientes(archivo_clientes)
generar_json_negociacion(archivo_negociacion)

# Generar el JSON de ofertas utilizando la ruta del archivo de negociaciones
ruta_negociacion = os.path.join(carpeta_data, 'negociacion.json')  # Ruta del JSON de negociaciones
generar_json_ofertas(ruta_negociacion)
