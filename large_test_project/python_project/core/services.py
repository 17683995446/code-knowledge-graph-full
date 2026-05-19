"""
Business logic services
"""
from typing import List, Optional, Dict, Any
from .models import User, Product, Order, OrderItem, BaseModel
from .exceptions import NotFoundError, ValidationError, AuthenticationError
from .utils import Logger, Cache


class BaseService:
    """Base service class"""
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.cache = Cache()


class UserService(BaseService):
    """User management service"""
    def __init__(self):
        super().__init__()
        self._users: Dict[int, User] = {}
        self._next_id = 1
    
    def create(self, username: str, email: str, password: str) -> User:
        """Create a new user"""
        if not username or not email:
            raise ValidationError("Username and email are required")
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.id = self._next_id
        self._next_id += 1
        self._users[user.id] = user
        self.logger.info(f"Created user: {username}")
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user = self._users.get(user_id)
        if not user:
            raise NotFoundError(f"User not found: {user_id}")
        return user
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._users.values())
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        user = self.get_by_id(user_id)
        for key, value in kwargs.items():
            if key in ["username", "email", "is_active", "roles"]:
                setattr(user, key, value)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user"""
        if user_id in self._users:
            del self._users[user_id]
            self.logger.info(f"Deleted user: {user_id}")
            return True
        return False
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        for user in self._users.values():
            if user.username == username and user.check_password(password):
                self.logger.info(f"Authenticated user: {username}")
                return user
        raise AuthenticationError("Invalid credentials")


class ProductService(BaseService):
    """Product management service"""
    def __init__(self):
        super().__init__()
        self._products: Dict[int, Product] = {}
        self._next_id = 1
    
    def create(self, name: str, description: str, price: float, 
               stock: int, category: str, tags: List[str] = None) -> Product:
        """Create a new product"""
        if price < 0:
            raise ValidationError("Price must be non-negative")
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            tags=tags or []
        )
        product.id = self._next_id
        self._next_id += 1
        self._products[product.id] = product
        self.logger.info(f"Created product: {name}")
        return product
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        product = self._products.get(product_id)
        if not product:
            raise NotFoundError(f"Product not found: {product_id}")
        return product
    
    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        return [p for p in self._products.values() if p.category == category]
    
    def search(self, query: str) -> List[Product]:
        """Search products"""
        query_lower = query.lower()
        results = []
        for product in self._products.values():
            if (query_lower in product.name.lower() or 
                query_lower in product.description.lower() or
                any(query_lower in tag.lower() for tag in product.tags)):
                results.append(product)
        return results
    
    def update_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """Update product stock"""
        product = self.get_by_id(product_id)
        if product.stock + quantity < 0:
            raise ValidationError("Insufficient stock")
        product.stock += quantity
        return product


class OrderService(BaseService):
    """Order management service"""
    def __init__(self, user_service: UserService, product_service: ProductService):
        super().__init__()
        self._user_service = user_service
        self._product_service = product_service
        self._orders: Dict[int, Order] = {}
        self._next_id = 1
    
    def create(self, user_id: int, items: List[Dict[str, Any]]) -> Order:
        """Create a new order"""
        # Validate user exists
        self._user_service.get_by_id(user_id)
        
        order_items = []
        total_amount = 0.0
        
        for item_data in items:
            product = self._product_service.get_by_id(item_data["product_id"])
            
            if product.stock < item_data["quantity"]:
                raise ValidationError(f"Insufficient stock for product {product.name}")
            
            order_item = OrderItem(
                product_id=product.id,
                quantity=item_data["quantity"],
                unit_price=product.price,
                product=product
            )
            
            order_items.append(order_item)
            total_amount += order_item.subtotal
        
        order = Order(
            user_id=user_id,
            status="pending",
            total_amount=total_amount,
            items=order_items
        )
        
        order.id = self._next_id
        self._next_id += 1
        self._orders[order.id] = order
        
        # Update stock
        for item in order_items:
            self._product_service.update_stock(item.product_id, -item.quantity)
        
        self.logger.info(f"Created order: {order.id}")
        return order
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        order = self._orders.get(order_id)
        if not order:
            raise NotFoundError(f"Order not found: {order_id}")
        return order
    
    def get_by_user(self, user_id: int) -> List[Order]:
        """Get orders by user"""
        return [o for o in self._orders.values() if o.user_id == user_id]
    
    def update_status(self, order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        order = self.get_by_id(order_id)
        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}")
        order.status = status
        self.logger.info(f"Updated order {order_id} status to: {status}")
        return order
