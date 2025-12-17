from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
import random


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: Optional[str] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    role: str = "user"
    is_active: bool = Field(True, alias="isActive")
    is_admin: bool = Field(False, alias="isAdmin")


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    gender: Optional[str] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    role: str = "seller"
    is_active: bool = True
    is_admin: bool = False
    password: str


class ClientCreate(BaseModel):
    identity: int = Field(alias="id")
    email: EmailStr
    first_name: str = Field(min_length=3, max_length=50, alias="firstName")
    last_name: str = Field(min_length=3, max_length=50, alias="lastName")
    gender: Optional[str] = None
    phone: Optional[str] = None
    role: str = "client"
    is_active: bool = True
    is_admin: bool = False
    password: str = Field(min_length=8, default=f"defaultpassword{random.randint(100000, 999999)}")


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    createdAt: datetime = Field(alias="created_at")
    updatedAt: Optional[datetime] = Field(None, alias="updated_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Product Schemas
class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    discount_percentage: float = Field(0.0, alias="discountPercentage")
    discount_money: float = Field(0.0, alias="discountMoney")
    stock: int = 0
    brand: Optional[str] = None
    sku: Optional[str] = None
    availability_status: str = Field("available", alias="availabilityStatus")
    minimum_order_quantity: int = Field(1, alias="minimumOrderQuantity")
    barcode: Optional[str] = None
    thumbnail: Optional[str] = None
    is_authorized: bool = Field(True, alias="isAuthorized")
    is_active: bool = Field(True, alias="isActive")


class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    discount_percentage: float = 0.0
    discount_money: float = 0.0
    stock: int = 0
    brand: Optional[str] = None
    sku: Optional[str] = None
    availability_status: str = "available"
    minimum_order_quantity: int = 1
    barcode: Optional[str] = None
    thumbnail: Optional[str] = None


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    discount_percentage: Optional[float] = None
    discount_money: Optional[float] = None
    stock: Optional[int] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    availability_status: Optional[str] = None
    minimum_order_quantity: Optional[int] = None
    barcode: Optional[str] = None
    thumbnail: Optional[str] = None
    is_authorized: Optional[bool] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Transaction Item Schemas
class TransactionItemBase(BaseModel):
    sku: Optional[str] = None
    quantity: int
    unit_price: float = Field(alias="unitPrice")
    discount: float = 0.0
    total: float


class TransactionItemCreate(BaseModel):
    sku: Optional[str] = None
    quantity: int
    unit_price: float
    discount: float = 0.0
    total: float


class TransactionItem(TransactionItemBase):
    id: int
    product_id: int = Field(alias="productId")
    product: Product
    total: float = Field(alias="total_price")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Transaction Payment Schemas
class TransactionPaymentBase(BaseModel):
    payment_method: str = Field(alias="paymentMethod")
    amount: float
    provider: Optional[str] = None


class TransactionPaymentCreate(BaseModel):
    payment_method: str
    amount: float
    provider: Optional[str] = None


class TransactionPayment(TransactionPaymentBase):
    id: int
    transaction_id: int = Field(alias="transactionId")
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Transaction Schemas
class TransactionBase(BaseModel):
    store_id: Optional[str] = Field(None, alias="storeId")
    pos_id: Optional[str] = Field(None, alias="posId")
    transaction_type: str = Field("SALE", alias="transactionType")
    transaction_number: Optional[str] = Field(None, alias="transactionNumber")
    transaction_date: Optional[datetime] = Field(None, alias="transactionDate")
    total_amount: float = Field(alias="totalAmount")
    customer_external_id: Optional[str] = Field(None, alias="customerExternalId")
    metadata: Optional[Dict[str, Any]] = None


class TransactionCreate(BaseModel):
    store_id: Optional[str] = None
    pos_id: Optional[str] = None
    transaction_type: str = "SALE"
    transaction_number: Optional[str] = None
    transaction_date: Optional[datetime] = None
    total_amount: float
    customer_external_id: Optional[str] = None
    status: str = "completed"
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    items: List[TransactionItemCreate]
    payments: List[TransactionPaymentCreate]


class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Transaction(TransactionBase):
    id: int
    user_id: int = Field(alias="userId")
    user: User
    items: List[TransactionItem]
    payments: List[TransactionPayment]
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: Optional[str] = None
    image: Optional[str] = None
    phone: Optional[str] = None
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken")


class RefreshResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")


class NewClientCreated(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    gender: Optional[str] = Field(None, alias="gender")
    phone: Optional[str] = Field(None, alias="phone")
    role: str = Field(alias="role")
    is_active: bool = Field(alias="isActive")
    is_admin: bool = Field(alias="isAdmin")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
