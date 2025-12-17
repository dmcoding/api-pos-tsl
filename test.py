from datetime import datetime, timedelta
import uuid
from app.services import tsl_converter

if __name__ == "__main__":
    
    user_id = 1
    uuid_number = str(uuid.uuid4().int)[-6:]
    transaction_dummy = {
        "store_id": "769f390e-295f-4c3f-99f9-8eaa9b3d406f",  # Store ID válido
        "pos_id": "POS-001",  # Cambia el ID del POS según tu caso
        "transaction_type": "VNT",  # Cambia el tipo de transacción si es necesario
        "transaction_number": f"{uuid_number}",  # Número de transacción único basado en timestamp
        "transaction_date": datetime.now().strftime("%Y%m%d"),  # Fecha actual en formato ISO8601
        "total_amount": 45523.0,  # Agrega el total de la transacción
        "customer_external_id": 1,  # Opcional: external_id del cliente desde el sistema externo
        "items": [
            {
                "barcode": "001234567890",  # Cambia por el SKU de un producto válido en tu base de datos
                "quantity": 2,  # Cambia la cantidad según el caso de prueba
                "unit_price": 12.5,  # Cambia el precio unitario
                "discount": 0.0,  # Cambia el descuento si aplica
                "total": 25.0  # Cambia el total si es necesario
            },
            {
                "barcode": "002234567890",  # Cambia por el SKU de un producto válido en tu base de datos
                "quantity": 1,  # Cambia la cantidad según el caso de prueba
                "unit_price": 12.5,  # Cambia el precio unitario
                "discount": 0.0,  # Cambia el descuento si aplica
                "total": 12.5  # Cambia el total si es necesario
            }
        ],
        "payments": [
            {
                "payment_method": "CASH",  # Cambia el método de pago si es necesario
                "amount": 5.5,  # Cambia el monto del pago
                "provider": "manual"  # Cambia el proveedor si aplica
            },
            {
                "payment_method": "CREDIT_CARD",  # Cambia el método de pago si es necesario
                "amount": 32.0,  # Cambia el monto del pago
                "provider": "Getnet"  # Cambia el proveedor si aplica
            }
        ],
        "metadata": {
            "notes": "Test transaction from simulated POS"  # Cambia las notas para otras pruebas
        },
        "authorized_supervisor": {
            "supervisor_id": 12345,
            "supervisor_name": "Supervisor Test"
        }
    }
    
    
    contable_date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    transaction_dummy["contable_date"] = contable_date
    transaction_dummy["transaction_hour"] = datetime.now().strftime("%H%M%S")
    transaction_dummy["seller_id"] = user_id
    transaction_dummy["document_type"] = "BLT"
    
    data_keys_parse_cabecera = {
        "Local": "store_id",
        "POS": "pos_id",
        "NumTrx": "transaction_number",
        "Fecha": "transaction_date",
        "FechaCont": "contable_date",
        "Hora": "transaction_hour",
        "Vendedor": "seller_id",
        "TipoTrx": "transaction_type",
        "TipoDoc": "document_type",
        "Total": "total_amount",
    }
    
    data_keys_parse_productos = {
        "CodProd": "barcode",
        "Cantidad": "quantity",
        "Precio": "unit_price",
        "Total": "total",
    }
    
    data_keys_parse_payment_methods = {
        "CodFP": "payment_method",
        "Monto": "amount",
    }
    
    data_keys_parse_impuestos = {
        "Codimp": "impuesto",
        "Porc": "porcentaje",
        "Monto": "monto",
    }
    
    data_keys_parse_descuentos = {
        "CodPromo": "promo_code",
        "CodDcto": "discount_code",
        "Porc": "percentage",
        "Monto": "amount",
        "Tipo": "type",
    }
    
    converter = tsl_converter.TSLConverter()
    

    try:
        
        ##
        # Pedido de venta
        ##
        # Se asignan los valores de la cabecera
        converter.assign_value_from_transaction(transaction_dummy, data_keys_parse_cabecera, tsl_converter.TSLConverterSubstringType.CABECERA)
        
        # TODO: Definir descuento si aplica a la transaccion completa (monto total de la transaccion)
        if False:
            converter.assign_value_from_transaction(transaction_dummy, data_keys_parse_impuestos, tsl_converter.TSLConverterSubstringType.IMPUESTOS)
        
        # Se asignan los valores de los productos
        for item in transaction_dummy["items"]:
            converter.assign_value_from_transaction(item, data_keys_parse_productos, tsl_converter.TSLConverterSubstringType.PRODUCTOS)
            #TODO: DEFINIR IMPUESTOS    
            if False:
                converter.assign_value_from_transaction(item, data_keys_parse_impuestos, tsl_converter.TSLConverterSubstringType.IMPUESTOS)
            #TODO: DEFINIR DESCUENTOS
            if False:
                converter.assign_value_from_transaction(item, data_keys_parse_descuentos, tsl_converter.TSLConverterSubstringType.DESCUENTOS)

        # Se asignan los valores de los pagos
        for payment in transaction_dummy["payments"]:
            converter.assign_value_from_transaction(payment, data_keys_parse_payment_methods, tsl_converter.TSLConverterSubstringType.FORMA_PAGO)
        
        # TODO: Definir el substring de pago
        if False:
            converter.assign_value_from_transaction(payment, data_keys_parse_payment_methods, tsl_converter.TSLConverterSubstringType.FORMA_PAGO)
        
        # TODO: Definir el substring de descuento si aplica a la forma de pago
        if False:
            converter.assign_value_from_transaction(payment, data_keys_parse_descuentos, tsl_converter.TSLConverterSubstringType.DESCUENTOS)
        
        converter.serialize_transaction()
        
        print(converter.value_converter)
        converter.save()
    except ValueError as e:
        print(f"Error assigning value from transaction: {e}")

