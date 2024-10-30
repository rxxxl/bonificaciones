/**
 * 
 * @initialize npm init (node js)
 * @dependency axios (npm i axios)
 * @returns 
 */

const axios = require("axios");
const data = require("../Json/sell_out_final.json");
const formatData = data.map((item) => {
    return {
        segmento: item["SEGMENT3"],
        tipo_documento: item["Tipo Documento"],
        segmentos_concatenados: item["CONCAT_SEGMENTS"],
        descripcion: item["DESCRIPTION"],
        nombre: item["NAME"],
        sucursal: item["Sucursal"],
        cliente_bandera: item["Clientes Carrito Flag"],
        tipo_pedido: item["TIPO_PEDIDO"],
        cadena_desc: item["CADENA_DESC"],
        deposito: item["DEPOSITO"],
        cliente: item["PARTY_NAME"],
        numero_cliente: item["PARTY_NUMBER"],
        tipo_cuenta: item["Tipo Cuenta"],
        canal: item["Canal"],
        perfil_nivel_cuenta: item["Perfil Nivel Cuenta"],
        cadena: item["Cadena"],
        numero_cuenta: item["ACCOUNT_NUMBER"],
        cuenta: item["Cuenta"],
        lista_precio: item["LISTA_PRECIOS"],
        laboratorio: item["Laboratorio"],
        division: item["División"],
        codigo_producto: item["Producto Código"],
        producto: item["Producto"],
        comprador: item["Comprador"],
        ffs: item["Fee for Service"],
        fecha: item["Fecha"],
        piezas_factura: item["Pzas Facturadas"],
        venta_neta: item["Venta neta"],
        segmento_4: item["SEGMENT4"],
        significado: item["MEANING"],
        numero_pedido: item["Numero Pedido"],
        oferta: item["Oferta"],
        oferta_factura: item["Oferta Factura"],
        descuento_factura: item["Descuento Factura"],
        costo_promedio: item["Costo Promedio"],
        trx_numero: item["TRX_NUMBER"],
        ean: item["EAN"],
        // "":item["Valuacion Unitaria"],
        validacion_cliente: item["Validacion Cliente"],
        llave: item["Llave"],
        cap: item["CAP"],
        oferta_calculada: item["OFERTA"],
        valor_valuacion: item["Valor Tipo de Valuacion"],
        tipo_valuacion: item["Tipo de Valuacion"],
        tipo_condicion: item["Tipo condicion costo"],
        total_valuacion: item["Costo Total"],
        valor_cap: item["Valor CAP"],
        costo_con_cap: item["Costo con CAP"],
        valor_oferta: item["Valor Oferta"],
        total_beneficio: item["Total Beneficio"],
    };
});

// Configure EndPoint for API APPSHEET
const apiUrl = "https://api.appsheet.com/api/v2/apps/";
const appIdD = "1f44e6a2-949e-4f4a-a658-0d7372ee52ce";
const applicationAccessKeyD =
    "V2-Oc8rQ-pPrdF-88FOU-CUJit-wB8S2-F8XYm-gnmTb-2RxRP";

// Define Options for URL
let options = {
    method: "post",
    contentType: "application/json",
    muteHttpExceptions: true, // Captura errores HTTP como excepciones.
};
// Estructure URL
const url = `${apiUrl}${appIdD}/tables/sell_out/Action?applicationAccessKey=${applicationAccessKeyD}`;

axios
    .post(
        url,
        {
            Action: "Add",
            Properties: {},
            Rows: formatData.slice(0, 1000)
        },
        options
    )
    .then(function (response) {
        console.log(response.status);
    })
    .catch(function (error) {
        console.log(error);
    });


