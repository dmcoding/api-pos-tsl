from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, auth
from ..services.tsl_converter import TSLConverter, TSLConverterSubstringType

router = APIRouter(tags=["transactions"])


@router.post("", response_model=schemas.Transaction, status_code=status.HTTP_201_CREATED)
def convert_transaction_tsl(
    transaction: schemas.TransactionTSLRequest,
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
        "Categoria": "category_id",
        "Cantidad": "quantity",
        "Precio": "unit_price",
        "Total": "total",
        "BrutoPositivo": "total_price",
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
        
        # transaction ya es un objeto Pydantic TransactionTSLRequest, usar directamente
        transaction_data = transaction.model_dump(mode='json')
        
        transaction_data["contable_date"] = transaction.transaction_date.strftime("%Y%m%d")
        
        transaction_data["transaction_date"] = transaction.transaction_date.strftime("%Y%m%d")
        transaction_data["transaction_hour"] = transaction.transaction_date.now().strftime("%H%M%S")
        transaction_data["seller_id"] = current_user.id
        
        transaction_data["total_amount"] = f"{transaction.total_amount:.3f}"
        
        ##
        # Pedido de venta
        ##
        # Se asignan los valores de la cabecera
        converter.assign_value_from_transaction(transaction_data, data_keys_parse_cabecera, TSLConverterSubstringType.CABECERA)
        
        # TODO: Definir descuento si aplica a la transaccion completa (monto total de la transaccion)
        if False:
            converter.assign_value_from_transaction(transaction_data, data_keys_parse_impuestos, TSLConverterSubstringType.IMPUESTOS)
        
        # Se asignan los valores de los productos
        if not transaction.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction must have at least one item")
        
        for item in transaction.items:
            # Usar by_alias=False para obtener los nombres de campo en lugar de los alias
            item_data = item.model_dump(mode='json') if hasattr(item, 'model_dump') else item
            # Si el item tiene 'sku' pero el mapeo busca 'barcode', usar 'sku' como 'barcode'
            if 'sku' in item_data and 'barcode' not in item_data:
                item_data['barcode'] = item_data.get('sku')
            
            if 'product' in item_data and 'category_id' in item_data['product']:
                item_data['category_id'] = item_data['product']['category_id']
                
            item_data['total_price'] = item_data['quantity'] * item_data['unit_price']
            
            item_data['total_price'] = f"{item_data['total_price']:.3f}"
            
            item_data['total'] = f"{item_data['total']:.3f}"
            item_data['discount'] = f"{item_data['discount']:.3f}"
            
            converter.assign_value_from_transaction(item_data, data_keys_parse_productos, TSLConverterSubstringType.PRODUCTOS)
            #TODO: DEFINIR IMPUESTOS    
            if False:
                converter.assign_value_from_transaction(item_data, data_keys_parse_impuestos, TSLConverterSubstringType.IMPUESTOS)
            #TODO: DEFINIR DESCUENTOS
            if False:
                converter.assign_value_from_transaction(item_data, data_keys_parse_descuentos, TSLConverterSubstringType.DESCUENTOS)

        # Se asignan los valores de los pagos
        if not transaction.payments:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction must have at least one payment")
        
        for payment in transaction.payments:
            # Usar by_alias=False para obtener los nombres de campo en lugar de los alias
            payment_data = payment.model_dump(mode='json') if hasattr(payment, 'model_dump') else payment
            payment_data['payment_method'] = '01'
            converter.assign_value_from_transaction(payment_data, data_keys_parse_payment_methods, TSLConverterSubstringType.FORMA_PAGO)
        
        # TODO: Definir el substring de pago
        if False:
            converter.assign_value_from_transaction(payment, data_keys_parse_payment_methods, TSLConverterSubstringType.FORMA_PAGO)
        
        # TODO: Definir el substring de descuento si aplica a la forma de pago
        if False:
            converter.assign_value_from_transaction(payment, data_keys_parse_descuentos, TSLConverterSubstringType.DESCUENTOS)
        
        converter.serialize_transaction()
        converter.save()
        
        return JSONResponse(
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