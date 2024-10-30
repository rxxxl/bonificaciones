import logging
import json  # Importa el módulo json para trabajar con archivos JSON.
import os  # Importa el módulo os para interactuar con el sistema operativo.
from datetime import datetime  # Importa la clase datetime del módulo datetime.

# Rutas de los archivos que se utilizarán en el script.
RUTA_ARCHIVO = ".\\json\\Base_Venta_detalle_Fanasa.json"  # Ruta del archivo sell_out.json.
RUTA_PRODUCTOS = ".\\json\\Catalogo_de_Productos.json"  # Ruta del archivo productos.json.
RUTA_CLIENTES = ".\\json\\Clientes_Aplicables.json"  # Ruta del archivo clientes_aplicables.json.
RUTA_OFERTAS = ".\\json\\ofertaSellOut.json"  # Ruta del archivo ofertas.json.
OUTPUT_FILE_PATH = "./json/sell_out_final.json"  # Ruta donde se guardará el archivo de salida.



# Configuración básica de logging
LOG_FILE_PATH = "./logs/app.log"
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.DEBUG,  # Puedes cambiar el nivel a INFO, ERROR, etc.
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Función para cargar archivos JSON
def cargar_json(ruta):
    """
    Carga un archivo JSON desde la ruta especificada.

    Args:
        ruta (str): La ruta del archivo JSON a cargar.

    Returns:
        dict: El contenido del archivo JSON como un diccionario.
        None: Si ocurre un error al cargar el archivo.

    Exceptions:
        FileNotFoundError: Si el archivo no se encuentra en la ruta especificada.
        json.JSONDecodeError: Si hay un error al decodificar el contenido del archivo JSON.
        Exception: Para cualquier otro tipo de error que ocurra durante la carga del archivo.
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"El archivo no se encontró: {ruta}")
    except json.JSONDecodeError:
        print(f"Error al decodificar JSON en el archivo: {ruta}")
    except Exception as e:
        print(f"Error al cargar el archivo {ruta}: {e}")
    return None

# Función para calcular los campos financieros
def calcular_campos_financieros(elemento):
    """
    Calcula y agrega varios campos financieros a un diccionario de elementos.
    Args:
        elemento (dict): Un diccionario que contiene los campos financieros necesarios.
    El diccionario `elemento` debe contener las siguientes claves para que los cálculos se realicen correctamente:
        - "CAP": El valor CAP como cadena que puede convertirse a float.
        - "Costo Total": El costo total como cadena que puede convertirse a float.
        - "Valor Tipo de Valuacion": El valor de tipo de valuación como cadena que puede convertirse a float.
        - "OFERTA": El valor de la oferta como cadena que puede convertirse a float.
    Los siguientes campos serán agregados al diccionario `elemento` si las claves necesarias están presentes:
        - "Valor CAP": El resultado de multiplicar el valor CAP por el costo total.
        - "Costo con CAP": El costo total menos el valor CAP.
        - "Valor Oferta": El resultado de multiplicar el costo con CAP por el valor de la oferta.
        - "Total Beneficio": La suma del valor CAP y el valor de la oferta.
    """
    if "CAP" in elemento and "Costo Total" in elemento:
        
        cap = float(elemento["CAP"])
        costo_reposicion = float(elemento["Valor Tipo de Valuacion"])\
        
        costo_total = float(elemento.get("Costo Total"))
        
        
        elemento["Valor CAP"] = cap * costo_total
        elemento["Costo con CAP"] = costo_total - elemento["Valor CAP"]

    if "Costo con CAP" in elemento and "OFERTA" in elemento:
        elemento["Valor Oferta"] = elemento["Costo con CAP"] * float(elemento["OFERTA"])

    if "Valor CAP" in elemento and "Valor Oferta" in elemento:
        elemento["Total Beneficio"] = elemento["Valor CAP"] + elemento["Valor Oferta"]
    
# Función para calcular las condiciones de costo según el tipo
def calcular_condicion_costo(primer_elemento):
    """
    Calcula el costo basado en el tipo de condición especificado en el diccionario `primer_elemento`.
    Args:
        primer_elemento (dict): Un diccionario que contiene los datos necesarios para calcular el costo. 
            Las claves esperadas en el diccionario incluyen:
            - "Tipo condicion costo" (str): El tipo de condición de costo a aplicar. Puede ser "% DESCUENTO SOBRE COSTO", "Costo Fijo", o "Monto Fijo".
            - "Pzas Facturadas" (float, opcional): El número de piezas facturadas. Valor predeterminado es 1 si no existe.
            - "Valor Tipo de Valuacion" (float, opcional): El valor del tipo de valuación. Valor predeterminado es 0.0 si no existe.
            - "Descuento Factura" (float, opcional): El descuento aplicado a la factura. Valor predeterminado es 0.0 si no existe.
            - "Costo Fijo" (float, opcional): El costo fijo aplicado. Valor predeterminado es 0.0 si no existe.
    Returns:
        None: La función modifica el diccionario `primer_elemento` en lugar de devolver un valor. 
        Agrega las siguientes claves al diccionario:
        - "Costo Total" (float): El costo total calculado (solo para "% DESCUENTO SOBRE COSTO").
        - "Valor condicion Costo" (float o str): El resultado del cálculo basado en la condición de costo.
    """
    tipo_condicion_costo = primer_elemento.get("Tipo condicion costo", None)
    resultado_condicion = 0

    if tipo_condicion_costo == "% DESCUENTO SOBRE COSTO":
        # Obtener los campos necesarios, asegurándonos de que sean numéricos
        piezas_facturadas = float(primer_elemento.get("Pzas Facturadas", 1))  # Valor predeterminado de 1 si no existe
        valor_tipo_valuacion = float(primer_elemento.get("Valor Tipo de Valuacion", 0.0))
        
        
        # Verificar si descuento_factura es None y manejarlo
        descuento_factura = primer_elemento.get("Descuento Factura")
        if descuento_factura is None:
            descuento_factura = 0.0
        else:
            descuento_factura = float(descuento_factura)
            
        resultado_condicion = (piezas_facturadas * valor_tipo_valuacion) - descuento_factura
        
        
        
        costo_total = piezas_facturadas * valor_tipo_valuacion 
        primer_elemento["Costo Total"] = costo_total
    elif tipo_condicion_costo == "Costo Fijo":
        #(pzas facturadas * valor tipo de valuacion) - (costo_fijo * pzas facturadas)
        piezas_facturadas = float(primer_elemento.get("Pzas Facturadas", 1))
        valor_tipo_valuacion = float(primer_elemento.get("Valor Tipo de Valuacion", 0.0))
        costo_fijo = float(primer_elemento.get("Costo Fijo", 0.0))
        
        
        resultado_condicion = (piezas_facturadas * valor_tipo_valuacion) - (costo_fijo * piezas_facturadas)
    elif tipo_condicion_costo == "Monto Fijo":
        # Realiza la operación correspondiente a "condicion3"
        resultado_condicion = "Hola monto fijo" # Ejemplo de cálculo
    else:
        # Si no se encuentra una condición válida, se puede definir un valor predeterminado
        resultado_condicion = "hOLA POR DEFECTO "

    # Agregar el resultado de la condición al JSON
    primer_elemento["Valor condicion Costo"] = resultado_condicion

# Función para procesar un elemento de sell_out
# Función para verificar si la fecha está dentro del rango de vigencia
def verificar_vigencia(fecha, fecha_inicio_vigencia, fecha_fin_vigencia):
    """
    Verifica si una fecha dada está dentro del rango de vigencia especificado.
    Args:
        fecha (str): La fecha a verificar en formato 'MM/DD/YYYY'.
        fecha_inicio_vigencia (str): La fecha de inicio de la vigencia en formato 'MM/DD/YYYY'.
        fecha_fin_vigencia (str): La fecha de fin de la vigencia en formato 'MM/DD/YYYY'.
    Returns:
        bool: True si la fecha está dentro del rango de vigencia, False en caso contrario.
    """
    # Convertir las fechas a objetos datetime
    formato_fecha = '%m/%d/%Y'  # Ajusta el formato según sea necesario
    fecha = datetime.strptime(fecha, formato_fecha)
    fecha_inicio_vigencia = datetime.strptime(fecha_inicio_vigencia, formato_fecha)
    fecha_fin_vigencia = datetime.strptime(fecha_fin_vigencia, formato_fecha)
    
    
    # Verificar si la fecha está en el rango
    return fecha_inicio_vigencia <= fecha <= fecha_fin_vigencia



# Función para procesar un elemento de sell_out
def procesar_elemento(primer_elemento, productos_dict, clientes_dict, ofertas_dict):
    """
    Procesa un elemento de datos y actualiza sus valores basándose en la información de productos, clientes y ofertas.
    Args:
        primer_elemento (dict): Diccionario que contiene los datos del elemento a procesar.
        productos_dict (dict): Diccionario que contiene información de productos.
        clientes_dict (dict): Diccionario que contiene información de clientes.
        ofertas_dict (dict): Diccionario que contiene información de ofertas.
    Returns:
        None: La función modifica el diccionario `primer_elemento` directamente.
    El procesamiento incluye:
        - Asignación de EAN y Valuacion Unitaria basándose en el código del producto.
        - Validación del cliente y generación de una llave única.
        - Verificación de ofertas aplicables y actualización de datos financieros y de condiciones de costo.
    """
    # Procesar Producto Código y EAN
    if "Producto Código" in primer_elemento:
        producto_codigo = primer_elemento["Producto Código"]
        codigo_base = producto_codigo[:-2]
        primer_elemento["EAN"] = codigo_base
        primer_elemento["Valuacion Unitaria"] = productos_dict.get(codigo_base, {}).get("Costo de Reposicion", None)

    # Procesar ACCOUNT_NUMBER y Validacion Cliente
    if "ACCOUNT_NUMBER" in primer_elemento:
        account_number = primer_elemento["ACCOUNT_NUMBER"]
        cliente_encontrado = clientes_dict.get(account_number, {})
        primer_elemento["Validacion Cliente"] = cliente_encontrado.get("Aplica", "No")
        retail_pago = cliente_encontrado.get("RETAIL PAGO", "No")
        
        primer_elemento["Llave"] = f"{retail_pago}{primer_elemento['EAN']}"

    # Procesar Llave y ofertas
    if "Llave" in primer_elemento:
        llave = primer_elemento["Llave"]
        oferta_encontrada = ofertas_dict.get(llave, {})
        
        # Verificar si hay una oferta para esa llave
        if oferta_encontrada:
            # Obtener la fecha del archivo 'Base_Venta_detalle_Fanasa.json'
            fecha = primer_elemento.get("Fecha", None)
            
            # Obtener las fechas de vigencia de la oferta
            fecha_inicio_vigencia = oferta_encontrada.get("Fecha inicio vigencia", None)
            fecha_fin_vigencia = oferta_encontrada.get("Fecha fin vigencia", None)
            
            # Verificar si las fechas son válidas y si la fecha está dentro del rango
            if fecha and fecha_inicio_vigencia and fecha_fin_vigencia and verificar_vigencia(fecha, fecha_inicio_vigencia, fecha_fin_vigencia):
                # Asignar datos de oferta si la fecha está dentro del rango de vigencia
                primer_elemento["CAP"] = float(oferta_encontrada.get("CAP", 0.0))
                primer_elemento["OFERTA"] = float(oferta_encontrada.get("Oferta", 0.0))

                # Obtener el "Tipo de Valuacion" desde el diccionario de ofertas
                tipo_valuacion = oferta_encontrada.get("Nombre regla", None)
                if tipo_valuacion and codigo_base in productos_dict:
                    primer_elemento["Valor Tipo de Valuacion"] = productos_dict[codigo_base].get(tipo_valuacion, None)
                    primer_elemento["Tipo de Valuacion"] = tipo_valuacion  # Agregamos el tipo de valuación
                
                # Obtener el "Tipo condicion costo" desde el diccionario de ofertas 
                tipo_condicion_costo = oferta_encontrada.get("Tipo condicion costo", None)
                if tipo_condicion_costo:
                    primer_elemento["Tipo condicion costo"] = tipo_condicion_costo

                # Calcular condiciones de costo
                calcular_condicion_costo(primer_elemento)

                # Calcular campos financieros
                calcular_campos_financieros(primer_elemento)
            else:
                print(f"La fecha {fecha} no está dentro del rango de vigencia para la oferta con llave {llave} fecha inicio {fecha_inicio_vigencia} {fecha_fin_vigencia}" )
        else:
            print(f"No se encontró oferta para la llave {llave} en el diccionario de ofertas.")
            
   

# Función principal para procesar los archivos
def procesar_archivos():
    """
    Procesa varios archivos JSON y realiza operaciones sobre los datos cargados.
    La función realiza las siguientes operaciones:
    1. Carga varios archivos JSON: datos, productos, clientes y ofertas.
    2. Verifica que todos los archivos se hayan cargado correctamente.
    3. Crea diccionarios a partir de los datos cargados para facilitar el acceso.
    4. Itera sobre los elementos de los datos cargados y los procesa.
    5. Guarda los datos modificados en un archivo de salida.
    Si alguno de los archivos no se puede cargar, la función imprime un mensaje de error y termina.
    Variables globales esperadas:
    - RUTA_ARCHIVO: Ruta del archivo JSON de datos.
    - RUTA_PRODUCTOS: Ruta del archivo JSON de productos.
    - RUTA_CLIENTES: Ruta del archivo JSON de clientes.
    - RUTA_OFERTAS: Ruta del archivo JSON de ofertas.
    - OUTPUT_FILE_PATH: Ruta del archivo JSON donde se guardarán los datos modificados.
    Returns:
        None
    """
    # Cargar los archivos
    data = cargar_json(RUTA_ARCHIVO)
    productos = cargar_json(RUTA_PRODUCTOS)
    clientes = cargar_json(RUTA_CLIENTES)
    ofertas = cargar_json(RUTA_OFERTAS)

    if not all([data, productos, clientes, ofertas]):
        print("No se pudieron cargar todos los archivos.")
        return

    # Crear diccionario de ofertas
    ofertas_dict = {oferta["Llave"]: oferta for oferta in ofertas}
    productos_dict = {producto["Producto Código"][:-2]: producto for producto in productos}
    clientes_dict = {cliente["NUMERO FARMACIA"]: cliente for cliente in clientes}

    total_elementos = len(data)

    for index, primer_elemento in enumerate(data[:total_elementos]):
        print(f"Procesando elemento {index + 1} de {total_elementos}")
        procesar_elemento(primer_elemento, productos_dict, clientes_dict, ofertas_dict)

    # Guardar el archivo modificado
    guardar_json(OUTPUT_FILE_PATH, data)

# Función para guardar el archivo JSON modificado
def guardar_json(ruta, data):
    """
    Guarda los datos proporcionados en un archivo JSON en la ruta especificada.

    Args:
        ruta (str): La ruta del archivo donde se guardarán los datos JSON.
        data (dict): Los datos que se guardarán en el archivo JSON.

    Raises:
        Exception: Si ocurre un error al intentar guardar el archivo.

    """
    try:
        with open(ruta, 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=4)
        print(f"Proceso completado. Datos guardados en: {ruta}")
    except Exception as e:
        print(f"Error al guardar el archivo {ruta}: {e}")

# Ejecutar la función principal
if __name__ == "__main__":
    procesar_archivos()