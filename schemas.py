"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Class name lowercased = collection name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# -------------------------
# Core ecommerce schemas
# -------------------------

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    slug: str = Field(..., description="URL-safe unique identifier")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in RON")
    image: Optional[str] = Field(None, description="Image URL")
    origin: Optional[str] = Field(None, description="Origin region (e.g., Kagoshima, Uji)")
    tasting_notes: Optional[str] = Field(None, description="Tasting notes")
    grade: Optional[str] = Field(None, description="Grade designation")
    weight_grams: Optional[int] = Field(30, ge=1, description="Net weight in grams")
    in_stock: bool = Field(True, description="Whether product is available")

class OrderItem(BaseModel):
    slug: str = Field(..., description="Product slug")
    quantity: int = Field(..., ge=1, le=100, description="Quantity ordered")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    items: List[OrderItem] = Field(..., description="List of items")
    name: str = Field(..., description="Customer name")
    email: EmailStr = Field(..., description="Customer email")
    phone: Optional[str] = Field(None, description="Customer phone")
    address: Optional[str] = Field(None, description="Shipping address")
    city: Optional[str] = Field(None, description="City")
    notes: Optional[str] = Field(None, description="Order notes")
    total_ron: Optional[float] = Field(None, ge=0, description="Computed server-side total in RON")
    status: str = Field("new", description="Order status")

class Lead(BaseModel):
    """
    Leads collection schema (B2B inquiries)
    Collection name: "lead"
    """
    name: str = Field(..., description="Contact name")
    email: EmailStr = Field(..., description="Contact email")
    client_type: str = Field(..., description="Restaurant/Cafenea, Retail, Persoană fizică")
    volume: Optional[str] = Field(None, description="Estimated monthly volume")
    packaging: Optional[str] = Field(None, description="Preferred packaging size")
    destination: Optional[str] = Field(None, description="HORECA/Retail/Acasă")
    message: Optional[str] = Field(None, description="Additional message")

# Note: The database viewer reads these via /schema endpoint if provided.
