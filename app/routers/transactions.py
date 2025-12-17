from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Request, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, auth
from ..services.tsl_converter import TSLConverter, TSLConverterSubstringType

router = APIRouter(tags=["transactions"])


@router.post("", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def convert_transaction_tsl(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    
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
    
    converter = TSLConverter()
    

    try:
        transaction: dict = request.json()
        
        ##
        # Pedido de venta
        ##
        # Se asignan los valores de la cabecera
        converter.assign_value_from_transaction(transaction, data_keys_parse_cabecera, TSLConverterSubstringType.CABECERA)
        
        # TODO: Definir descuento si aplica a la transaccion completa (monto total de la transaccion)
        if False:
            converter.assign_value_from_transaction(transaction, data_keys_parse_impuestos, TSLConverterSubstringType.IMPUESTOS)
        
        # Se asignan los valores de los productos
        for item in transaction["items"]:
            converter.assign_value_from_transaction(item, data_keys_parse_productos, TSLConverterSubstringType.PRODUCTOS)
            #TODO: DEFINIR IMPUESTOS    
            if False:
                converter.assign_value_from_transaction(item, data_keys_parse_impuestos, TSLConverterSubstringType.IMPUESTOS)
            #TODO: DEFINIR DESCUENTOS
            if False:
                converter.assign_value_from_transaction(item, data_keys_parse_descuentos, TSLConverterSubstringType.DESCUENTOS)

        # Se asignan los valores de los pagos
        for payment in transaction["payments"]:
            converter.assign_value_from_transaction(payment, data_keys_parse_payment_methods, TSLConverterSubstringType.FORMA_PAGO)
        
        # TODO: Definir el substring de pago
        if False:
            converter.assign_value_from_transaction(payment, data_keys_parse_payment_methods, TSLConverterSubstringType.FORMA_PAGO)
        
        # TODO: Definir el substring de descuento si aplica a la forma de pago
        if False:
            converter.assign_value_from_transaction(payment, data_keys_parse_descuentos, TSLConverterSubstringType.DESCUENTOS)
        
        converter.serialize_transaction()
        
        return Response(
            status_code=status.HTTP_200_OK, 
            content={
                "status": "success",
                "message": "Transaction converted successfully",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": converter.value_converter
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error assigning value from transaction: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error converting transaction: {e}")