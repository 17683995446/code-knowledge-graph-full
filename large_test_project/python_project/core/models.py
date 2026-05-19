"""
Data models for the system
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib


@dataclass
class BaseModel:
    """Base model class"""
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class User(BaseModel):
    """User entity"""
    username: str = ""
    email: str = ""
    password_hash: Optional[str] = None
    is_active: bool = True
    roles: List[str] = field(default_factory=list)
    
    def set_password(self, password: str):
        """Set user password"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check user password"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


@dataclass
class Product(BaseModel):
    """Product entity"""
    name: str = ""
    description: str = ""
    price: float = 0.0
    stock: int = 0
    category: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class OrderItem:
    """Order item entity"""
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[Product] = None
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal"""
        return self.quantity * self.unit_price


@dataclass
class Order(BaseModel):
    """Order entity"""
    user_id: Optional[int] = None
    status: str = "pending"
    total_amount: float = 0.0
    items: List[OrderItem] = field(default_factory=list)
    user: Optional[User] = None
    
    def calculate_total(self) -> float:
        """Calculate total amount"""
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount
