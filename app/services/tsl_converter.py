from datetime import datetime
from enum import Enum
import os


class TSLConverterSubstringType(Enum):
    CABECERA = "cabecera"
    PRODUCTOS = "productos"
    DESCUENTOS = "descuentos"
    IMPUESTOS = "impuestos"
    FORMA_PAGO = "forma_pago"
    EXCEPCIONES = "excepciones"
    SUPERVISOR = "supervisor"
    SISTEMA = "sistema"
    REGISTRO_Z = "registro_z"
    RESUMEN_MONTOS_VENTAS = "resumen_montos_ventas"
    CREACION_ACTUALIZACION_CLIENTE_FIDELIZADO = "creacion_actualizacion_cliente_fidelizado"
    DATOS_COMPLEMENTARIOS_DESPACHOS = "datos_complementarios_despachos"
    DATOS_COMPLEMENTARIOS_DEVOLUCIONES = "datos_complementarios_devoluciones"
    DATOS_COMPLEMENTARIOS_RECARGA_TELEFONICA = "datos_complementarios_recarga_telefonica"


class TSLConverter:
    """
    Clase para convertir una transaccion de la api a un archivo TSL
    
    Ejemplo de uso:
    ```python
    converter = TSLConverter()
    converter.assign_value_from_transaction(transaction, data_keys_parse_cabecera, tsl_converter.TSLConverterSubstringType.CABECERA)
    converter.serialize_transaction()
    converter.save()
    ```
    
    Existen 4 tipos de transacciones:
    - Venta
        Ejemplo: 
            "00FSf2FSf3...", "01FSf2FSf3...", "02FS0FSf3...", "03FSf2FSf3...", "04FS1FSf3..."...0D0A

    - Dotación
        Ejemplo: 
            “00FSf2FSf3...”,”04FS1FSf3...”0D0A
    
    - Retiro
        Ejemplo: 
            “00FSf2FSf3...”,”04FS1FSf3...”0D0A
    
    - Recaudación
        Ejemplo: 
            “00FSf2FSf3...”, ”99FS08FSf3...”,”01FSf2FSf3...”,”04FS1FSf3...”...0D0A
            
    Para cada tipo de transaccion, se debe asignar los valores de la transaccion a los substrings correspondientes.
    
    Para la venta, se debe asignar los valores de la transaccion a los substrings correspondientes.
    """

    # 1. Definición de Separadores
    FS = '\x1c'  # Separador de Campo (0x1Ch)
    CRLF = '\r\n'  # Fin de Transacción (0x0D0Ah)

    
    _value_converter = None
    
    @property
    def value_converter(self):
        return self._value_converter
    
    # 2. Datos de la Transacción de Venta (VNT) en Python
    # Solo contiene los atributos de la transaccion que se van a asignar a los substrings correspondientes.
    # Solo son los indicados como obligatorios para la transaccion según lo indica la documentación del TSL.
    data_transaction = {
        TSLConverterSubstringType.CABECERA: {
            "TipoReg": "00",
            "Pais": "0", # 0 = Chile
            "Origen": "1", # 1 = Tienda
            "Local": "33", # TODO: Definir el local (se obtiene de la api o se pondra hardcodeado en algun archivo de configuracion)
            "POS": "1", # TODO: Definir la caja (se obtiene de la api o se pondra hardcodeado en algun archivo de configuracion)
            "NroDoc": 12345, # TODO: Definir
            "NumTrx": None, # Se obtiene del json de la transaccion
            "Fecha": None, # Se obtiene del json de la transaccion Formato YYYYMMDD
            "FechaCont": None, # TODO: Definir dummy hoy más un día
            "Hora": None, # Se obtiene del json de la transaccion Formato HHMMSS
            "Turno": 1, # TODO: Definir
            "Cajero": "12345", # TODO: Definir el valor del cajero (se obtiene de la api o se pondra hardcodeado en algun archivo de configuracion)
            "Vendedor": None,
            "TipoTrx": None,
            "TipoDoc": None, # TODO: Definir el tipo de documento (se obtiene del json de la transaccion)
            "Total": None,
        },
        TSLConverterSubstringType.PRODUCTOS: {
            "TipoReg": "01",
            "CodProd": None,
            "Categoría": "cat_producto", # TODO: Definir el valor de la categoria
            "Cantidad": None,
            "BrutoPositivo": 10000.000, # TODO: Definir el valor de la lista de precios
            "BrutoNegativo": -10000.000,  # TODO: Definir el valor de la lista de precios
            "Unidades": 0, # TODO: Definir el valor de las unidades (0 = Unidades, 1 = Gramos, 2 = Litros)
            "Total": None,
            "TipoProducto": "1", # TODO: Definir el tipo de producto
            "Anulado": 0, # TODO: Definir si el producto esta anulado (0 = No anulado, 1 = Anulado, 2 = Devolucion)
            "Despacho": "1", # TODO: Definir si el producto es un despacho (1 = Despacho, 0 = No despacho)
            "Precio": None,
        },
        TSLConverterSubstringType.DESCUENTOS: {
            "TipoReg": "02",
            "Aplicado": "0", # TODO: Definir si el descuento esta aplicado (0 = Producto, 1 = Forma de pago, 2 = Total de la venta)
            "CodPromo": None,
            "CodDcto": None,
            "Porc": None,
            "Monto": None,
            "Tipo": "N", # TODO: Definir el tipo de descuento (N = Normal, P = Prorrateo)
        },
        TSLConverterSubstringType.IMPUESTOS: {
            "TipoReg": "03",
            "Aplica": 2, # TODO: Definir si el impuesto esta aplicado (1 = Producto, 2 = Total de la venta)
            "Codimp": "00", # TODO: Definir el codigo del impuesto (00 = IVA, 01 = Exento)
            "Porc": 190, # TODO: Definir el porcentaje del impuesto formato XXXY (190 = 19%)
            "Monto": None, # Formato XXXXXXXXYY (10000000 = 100000.00)
        },
        TSLConverterSubstringType.FORMA_PAGO: {
            "TipoReg": "04",
            "CodFP": None,
            "Monto": None,
            "CodMoneda": 1, #TODO: Definir la moneda
            "Anulado": 0, #TODO: Definir si el pago esta anulado
        },
        TSLConverterSubstringType.EXCEPCIONES: {
            "TipoReg": "05",
            "Codexcep": None,
            "Descripcion": None,
        },
        TSLConverterSubstringType.SUPERVISOR: {
            "TipoReg": "06",
            "CodSup": 12345, # TODO: Definir el valor del supervisor
            "Observacion": None,
        },
        TSLConverterSubstringType.SISTEMA: {
            "TipoReg": "07",
            "Impresora": 12345, # TODO: Definir el valor de la impresora
            "Version": None,
        },
        TSLConverterSubstringType.REGISTRO_Z: {
            "TipoReg": "09",
            "FechaCont": 12345, # TODO: Definir el valor del registro Z
            "FechaTrx": None, # TODO: Definir el valor de la fecha de la transaccion
            "HoraTrx": None, # TODO: Definir el valor de la hora de la transaccion
            "CantZ": None, # TODO: Definir el valor de la cantidad de registros Z
            "MontoZ": None, # TODO: Definir el valor de la cantidad de registros Z
        },
        TSLConverterSubstringType.RESUMEN_MONTOS_VENTAS: {
            "TipoReg": "11",
            "Tipo_Trx": None, # TODO: Definir el valor del registro Z
            "Tipo_Doc": None, # TODO: Definir el valor del tipo de documento
            "Forma_pago": None, # TODO: Definir el valor de la forma de pago
            "Total": None, # TODO: Definir el valor del total
        },
        TSLConverterSubstringType.CREACION_ACTUALIZACION_CLIENTE_FIDELIZADO: {
            "TipoReg": "99",
            "SubTipo": "03", # TODO: Definir el valor de la fecha
            "RutCliente": None, # TODO: Definir el valor del numero de referencia
            "NombreCliente": None, # TODO: Definir el valor del tipo de pedido
            "Mail": None, # TODO: Definir el valor del producto
            "Direccion": None, # TODO: Definir el valor de la posicion
            "Comuna": None, # TODO: Definir el valor de la posicion
        },
        TSLConverterSubstringType.DATOS_COMPLEMENTARIOS_DESPACHOS: {
            "TipoReg": "99",
            "SubTipo": "06", # TODO: Definir el valor de la fecha
            "RutCliente": None, # TODO: Definir el valor del numero de referencia
            "NombreCliente": None, # TODO: Definir el valor del tipo de pedido
            "Mail": None, # TODO: Definir el valor del producto
            "Direccion": None, # TODO: Definir el valor de la posicion
            "Comuna": None, # TODO: Definir el valor de la posicion
            "Ciudad": None, # TODO: Definir el valor de la posicion
            "Fono": None, # TODO: Definir el valor de la posicion
            "FechaDespacho": None, # TODO: Definir el valor de la posicion
            "LocalOrigen": None, # TODO: Definir el valor de la posicion
            "Cantidad": None, # TODO: Definir el valor de la posicion
            "Region": None, # TODO: Definir el valor de la posicion
            "Mail2": None, # TODO: Definir el valor de la posicion
            "Fono2": None, # TODO: Definir el valor de la posicion
            "PosProducto": None, # TODO: Definir el valor de la posicion
        },
        TSLConverterSubstringType.DATOS_COMPLEMENTARIOS_DEVOLUCIONES: {
            "TipoReg": "99",
            "SubTipo": "07", # TODO: Definir el valor de la fecha
            "CodProd": None, # TODO: Definir el valor del codigo del producto
            "Local": None, # TODO: Definir el valor del local de origen
            "Pos": None, # TODO: Definir el valor de la posicion
            "NumTRX": None, # TODO: Definir el valor del numero de transaccion
            "FechaTRX": None, # TODO: Definir el valor de la fecha
            "PosicionOri": None, # TODO: Definir el valor de la posicion
        },
        TSLConverterSubstringType.DATOS_COMPLEMENTARIOS_RECARGA_TELEFONICA: {
            "TipoReg": "99",
            "SubTipo": "08", # TODO: Definir el valor de la fecha
            "Operador": None, # TODO: Definir el valor del numero de referencia
            "Telefono": None, # TODO: Definir el valor del telefono
            "CodAutorizacion": None, # TODO: Definir el valor del codigo de autorizacion
            "CodMC": None, # TODO: Definir el valor del codigo de moneda
        },
        
    }
    
    
    _data_transaction_info = []

    def serialize_transaction(self):
        values = [
            f'"{self.FS.join(f"{val}" for val in value.values())}"'
            for value in self._data_transaction_info
        ]
        self._value_converter = f"{",".join(values)}{self.CRLF}"
    

    def assign_value_from_transaction(self, transaction: dict, assign_keys: dict, type_substring: TSLConverterSubstringType) -> dict:
        _data_transaction_temporal = self.data_transaction[type_substring]
        
        for to_key, from_key in assign_keys.items():
            if from_key not in transaction:
                raise ValueError(f"Key {to_key} not found in transaction")
            
            if to_key not in self.data_transaction[type_substring]:
                raise ValueError(f"Key {from_key} not found in {type_substring}")
            
            _data_transaction_temporal[to_key] = transaction[from_key]
            
        self._data_transaction_info.append(_data_transaction_temporal)
        
    
    def save(self):
        path = os.path.join(os.getcwd(), "tsl_files", f"tsl_output_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        
        with open(path, "w") as file:
            file.write(self._value_converter)
        
