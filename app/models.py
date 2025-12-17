from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
    

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    phone = Column(String(20), nullable=True)

    # Relaciones
    transactions = relationship("Transaction", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    discount_money = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    brand = Column(String(100))
    sku = Column(String(50), unique=True, index=True)
    availability_status = Column(String(20), default="available")  # available, out_of_stock, discontinued
    minimum_order_quantity = Column(Integer, default=1)
    barcode = Column(String(50), unique=True)
    thumbnail = Column(String(500))  # URL de la imagen
    is_authorized = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    transaction_items = relationship("TransactionItem", back_populates="product")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_id = Column(String(255), nullable=True)  # Store ID from external system
    pos_id = Column(String(50), nullable=True)  # POS terminal ID
    transaction_type = Column(String(20), default="SALE")  # SALE, RETURN, REFUND, etc.
    transaction_number = Column(String(100), unique=True, index=True)  # Unique transaction number
    transaction_date = Column(DateTime(timezone=True), nullable=True)  # Transaction date from POS
    total_amount = Column(Float, nullable=False)
    customer_external_id = Column(String(100), nullable=True)  # External customer ID
    status = Column(String(20), default="completed")  # pending, completed, cancelled
    notes = Column(Text)
    # metadata = Column(JSON, nullable=True)  # Additional metadata as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")
    payments = relationship("TransactionPayment", back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku = Column(String(50), nullable=True)  # Product SKU for reference
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)  # Discount amount
    total_price = Column(Float, nullable=False)

    # Relaciones
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")


class TransactionPayment(Base):
    __tablename__ = "transaction_payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    payment_method = Column(String(50), nullable=False)  # CASH, CREDIT_CARD, DEBIT_CARD, etc.
    amount = Column(Float, nullable=False)
    provider = Column(String(100), nullable=True)  # Payment provider (Getnet, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    transaction = relationship("Transaction", back_populates="payments")
