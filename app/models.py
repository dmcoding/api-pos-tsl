from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def model_dump(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=True)  # male, female, other
    image = Column(String(500),)
    role = Column(String(20), default="user")  # user, admin, manager, etc.
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    phone = Column(String(20), nullable=True)

    # Relaciones
    transactions = relationship("Transaction", back_populates="user")


class Category(BaseModel):
    __tablename__ = "categories"

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relaciones
    products = relationship("Product", back_populates="category")


class Product(BaseModel):
    __tablename__ = "products"

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    price = Column(Numeric(10, 3), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0.0)
    discount_money = Column(Numeric(10, 3), default=0.0)
    stock = Column(Integer, default=0)
    brand = Column(String(100))
    sku = Column(String(50), unique=True, index=True)
    availability_status = Column(String(20), default="available")  # available, out_of_stock, discontinued
    minimum_order_quantity = Column(Integer, default=1)
    barcode = Column(String(50), unique=True)
    thumbnail = Column(String(500))  # URL de la imagen
    is_authorized = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Relaciones
    transaction_items = relationship("TransactionItem", back_populates="product")
    category = relationship("Category", back_populates="products")


class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_id = Column(String(255), nullable=True)  # Store ID from external system
    pos_id = Column(String(50), nullable=True)  # POS terminal ID
    transaction_type = Column(String(20), default="PVT")  # PVT, RETURN, REFUND, etc.
    transaction_number = Column(String(100), unique=True, index=True)  # Unique transaction number
    transaction_date = Column(DateTime(timezone=True), nullable=True)  # Transaction date from POS
    total_amount = Column(Numeric(10, 3), nullable=False)
    customer_external_id = Column(String(100), nullable=True)  # External customer ID
    status = Column(String(20), default="completed")  # pending, completed, cancelled
    notes = Column(Text)
    document_type = Column(String(20))  # BLT, NOTA_CREDITO, NOTA_DEBITO, etc.
    # metadata = Column(JSON, nullable=True)  # Additional metadata as JSON

    # Relaciones
    user = relationship("User", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")
    payments = relationship("TransactionPayment", back_populates="transaction", cascade="all, delete-orphan")
    tsl_data = relationship("TransactionTSLData", back_populates="transaction", cascade="all, delete-orphan")
    
    def model_dump(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "store_id": self.store_id,
            "pos_id": self.pos_id,
            "transaction_type": self.transaction_type,
            "transaction_number": self.transaction_number,
            "transaction_date": self.transaction_date,
            "total_amount": self.total_amount,
            "customer_external_id": self.customer_external_id,
            "status": self.status,
            "notes": self.notes,
            "items": [item.model_dump() for item in self.items],
            "payments": [payment.model_dump() for payment in self.payments]
        }


class TransactionItem(BaseModel):
    __tablename__ = "transaction_items"

    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku = Column(String(50), nullable=True)  # Product SKU for reference
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 3), nullable=False)
    discount = Column(Numeric(10, 3), default=0.0)  # Discount amount
    total_price = Column(Numeric(10, 3), nullable=False)

    # Relaciones
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")
    
    created_at = None
    updated_at = None
    
    def model_dump(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "sku": self.sku,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "discount": self.discount,
            "total_price": self.total_price,
            "transaction": self.transaction.model_dump(),
            "product": self.product.model_dump()
        }

class TransactionPayment(BaseModel):
    __tablename__ = "transaction_payments"

    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    payment_method = Column(String(50), nullable=False)  # CASH, CREDIT_CARD, DEBIT_CARD, etc.
    amount = Column(Numeric(10, 3), nullable=False)
    provider = Column(String(100), nullable=True)  # Payment provider (Getnet, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    transaction = relationship("Transaction", back_populates="payments")

    updated_at = None
    
    def model_dump(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "payment_method": self.payment_method,
            "amount": self.amount,
            "provider": self.provider,
        }
    
class TransactionTSLData(BaseModel):
    __tablename__ = "transaction_tsl_data"

    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    tsl_data = Column(Text, nullable=True)
    is_tsl_data_valid = Column(Boolean, default=False)
    tsl_data_validation_message = Column(Text, nullable=True)
    tsl_data_validation_status = Column(String(20), default="pending")  # pending, valid, invalid
    tsl_data_validation_date = Column(DateTime(timezone=True), nullable=True)
    is_tsl_data_sent = Column(Boolean, default=False)
    tsl_data_sent_date = Column(DateTime(timezone=True), nullable=True)
    tsl_data_sent_message = Column(Text, nullable=True)
    tsl_data_sent_status = Column(String(20), default="pending")  # pending, sent, failed

    # Relaciones
    transaction = relationship("Transaction", back_populates="tsl_data")

    updated_at = None
    
    def model_dump(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "tsl_data": self.tsl_data,
            "is_tsl_data_valid": self.is_tsl_data_valid,
            "tsl_data_validation_message": self.tsl_data_validation_message,
            "tsl_data_validation_status": self.tsl_data_validation_status,
            "tsl_data_validation_date": self.tsl_data_validation_date,
            "is_tsl_data_sent": self.is_tsl_data_sent,
            "tsl_data_sent_date": self.tsl_data_sent_date,
            "tsl_data_sent_message": self.tsl_data_sent_message,
            "tsl_data_sent_status": self.tsl_data_sent_status,
        }