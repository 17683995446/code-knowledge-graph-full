#!/usr/bin/env python3
"""
生成超大规模复杂测试项目的脚本
用于深度测试代码知识图谱系统
"""
import os
import sys
from pathlib import Path


def create_python_test_project(base_path: Path):
    """创建复杂的Python测试项目"""
    project_dir = base_path / "python_project"
    project_dir.mkdir(exist_ok=True, parents=True)
    
    # 创建核心模块
    core_dir = project_dir / "core"
    core_dir.mkdir(exist_ok=True)
    (core_dir / "__init__.py").write_text("""
\"\"\"Core module\"\"\"
from .models import User, Order, Product
from .services import UserService, OrderService, ProductService
from .utils import Logger, Config, Cache
from .exceptions import ValidationError, NotFoundError, AuthenticationError

__all__ = [
    "User", "Order", "Product",
    "UserService", "OrderService", "ProductService",
    "Logger", "Config", "Cache",
    "ValidationError", "NotFoundError", "AuthenticationError"
]
""")
    
    (core_dir / "models.py").write_text("""\"\"\"
Data models for the system
\"\"\"
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib


@dataclass
class BaseModel:
    \"\"\"Base model class\"\"\"
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Convert model to dictionary\"\"\"
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class User(BaseModel):
    \"\"\"User entity\"\"\"
    username: str = ""
    email: str = ""
    password_hash: Optional[str] = None
    is_active: bool = True
    roles: List[str] = field(default_factory=list)
    
    def set_password(self, password: str):
        \"\"\"Set user password\"\"\"
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        \"\"\"Check user password\"\"\"
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


@dataclass
class Product(BaseModel):
    \"\"\"Product entity\"\"\"
    name: str = ""
    description: str = ""
    price: float = 0.0
    stock: int = 0
    category: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class OrderItem:
    \"\"\"Order item entity\"\"\"
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[Product] = None
    
    @property
    def subtotal(self) -> float:
        \"\"\"Calculate subtotal\"\"\"
        return self.quantity * self.unit_price


@dataclass
class Order(BaseModel):
    \"\"\"Order entity\"\"\"
    user_id: Optional[int] = None
    status: str = "pending"
    total_amount: float = 0.0
    items: List[OrderItem] = field(default_factory=list)
    user: Optional[User] = None
    
    def calculate_total(self) -> float:
        \"\"\"Calculate total amount\"\"\"
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount
""")
    
    (core_dir / "services.py").write_text("""\"\"\"
Business logic services
\"\"\"
from typing import List, Optional, Dict, Any
from .models import User, Product, Order, OrderItem, BaseModel
from .exceptions import NotFoundError, ValidationError, AuthenticationError
from .utils import Logger, Cache


class BaseService:
    \"\"\"Base service class\"\"\"
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.cache = Cache()


class UserService(BaseService):
    \"\"\"User management service\"\"\"
    def __init__(self):
        super().__init__()
        self._users: Dict[int, User] = {}
        self._next_id = 1
    
    def create(self, username: str, email: str, password: str) -> User:
        \"\"\"Create a new user\"\"\"
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
        \"\"\"Get user by ID\"\"\"
        user = self._users.get(user_id)
        if not user:
            raise NotFoundError(f"User not found: {user_id}")
        return user
    
    def get_all(self) -> List[User]:
        \"\"\"Get all users\"\"\"
        return list(self._users.values())
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        \"\"\"Update user information\"\"\"
        user = self.get_by_id(user_id)
        for key, value in kwargs.items():
            if key in ["username", "email", "is_active", "roles"]:
                setattr(user, key, value)
        return user
    
    def delete(self, user_id: int) -> bool:
        \"\"\"Delete user\"\"\"
        if user_id in self._users:
            del self._users[user_id]
            self.logger.info(f"Deleted user: {user_id}")
            return True
        return False
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        \"\"\"Authenticate user\"\"\"
        for user in self._users.values():
            if user.username == username and user.check_password(password):
                self.logger.info(f"Authenticated user: {username}")
                return user
        raise AuthenticationError("Invalid credentials")


class ProductService(BaseService):
    \"\"\"Product management service\"\"\"
    def __init__(self):
        super().__init__()
        self._products: Dict[int, Product] = {}
        self._next_id = 1
    
    def create(self, name: str, description: str, price: float, 
               stock: int, category: str, tags: List[str] = None) -> Product:
        \"\"\"Create a new product\"\"\"
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
        \"\"\"Get product by ID\"\"\"
        product = self._products.get(product_id)
        if not product:
            raise NotFoundError(f"Product not found: {product_id}")
        return product
    
    def get_by_category(self, category: str) -> List[Product]:
        \"\"\"Get products by category\"\"\"
        return [p for p in self._products.values() if p.category == category]
    
    def search(self, query: str) -> List[Product]:
        \"\"\"Search products\"\"\"
        query_lower = query.lower()
        results = []
        for product in self._products.values():
            if (query_lower in product.name.lower() or 
                query_lower in product.description.lower() or
                any(query_lower in tag.lower() for tag in product.tags)):
                results.append(product)
        return results
    
    def update_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        \"\"\"Update product stock\"\"\"
        product = self.get_by_id(product_id)
        if product.stock + quantity < 0:
            raise ValidationError("Insufficient stock")
        product.stock += quantity
        return product


class OrderService(BaseService):
    \"\"\"Order management service\"\"\"
    def __init__(self, user_service: UserService, product_service: ProductService):
        super().__init__()
        self._user_service = user_service
        self._product_service = product_service
        self._orders: Dict[int, Order] = {}
        self._next_id = 1
    
    def create(self, user_id: int, items: List[Dict[str, Any]]) -> Order:
        \"\"\"Create a new order\"\"\"
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
        \"\"\"Get order by ID\"\"\"
        order = self._orders.get(order_id)
        if not order:
            raise NotFoundError(f"Order not found: {order_id}")
        return order
    
    def get_by_user(self, user_id: int) -> List[Order]:
        \"\"\"Get orders by user\"\"\"
        return [o for o in self._orders.values() if o.user_id == user_id]
    
    def update_status(self, order_id: int, status: str) -> Optional[Order]:
        \"\"\"Update order status\"\"\"
        order = self.get_by_id(order_id)
        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}")
        order.status = status
        self.logger.info(f"Updated order {order_id} status to: {status}")
        return order
""")
    
    (core_dir / "utils.py").write_text("""\"\"\"
Utility functions and helpers
\"\"\"
import time
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime


class Logger:
    \"\"\"Simple logger class\"\"\"
    def __init__(self, name: str):
        self.name = name
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().isoformat()
        print(f\"[{timestamp}] [{level}] [{self.name}] {message}\")
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warning(self, message: str):
        self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)
    
    def debug(self, message: str):
        self._log("DEBUG", message)


class Cache:
    \"\"\"Simple in-memory cache\"\"\"
    def __init__(self, ttl: int = 300):
        self._cache: Dict[str, Any] = {}
        self._ttl = ttl
        self._timestamps: Dict[str, float] = {}
        self._logger = Logger("Cache")
    
    def get(self, key: str) -> Optional[Any]:
        \"\"\"Get value from cache\"\"\"
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                self.delete(key)
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        \"\"\"Set value in cache\"\"\"
        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._logger.debug(f"Cached: {key}")
    
    def delete(self, key: str):
        \"\"\"Delete value from cache\"\"\"
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
            self._logger.debug(f"Deleted cache: {key}")
    
    def clear(self):
        \"\"\"Clear all cache\"\"\"
        self._cache.clear()
        self._timestamps.clear()
        self._logger.info("Cache cleared")


class Config:
    \"\"\"Configuration management\"\"\"
    _config: Dict[str, Any] = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "mydb"
        },
        "cache": {
            "ttl": 300
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000
        }
    }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        \"\"\"Get configuration value\"\"\"
        keys = key.split(".")
        value = cls._config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    @classmethod
    def set(cls, key: str, value: Any):
        \"\"\"Set configuration value\"\"\"
        keys = key.split(".")
        current = cls._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value


def generate_id() -> str:
    \"\"\"Generate unique ID\"\"\"
    return hashlib.md5(str(time.time()).encode()).hexdigest()


def validate_email(email: str) -> bool:
    \"\"\"Validate email format\"\"\"
    if "@" not in email:
        return False
    domain = email.split("@")[1]
    if "." not in domain:
        return False
    return True


def format_price(price: float) -> str:
    \"\"\"Format price as currency\"\"\"
    return f"${price:.2f}"
""")
    
    (core_dir / "exceptions.py").write_text("""\"\"\"
Custom exceptions
\"\"\"


class AppException(Exception):
    \"\"\"Base application exception\"\"\"
    pass


class ValidationError(AppException):
    \"\"\"Validation error\"\"\"
    pass


class NotFoundError(AppException):
    \"\"\"Resource not found error\"\"\"
    pass


class AuthenticationError(AppException):
    \"\"\"Authentication error\"\"\"
    pass


class AuthorizationError(AppException):
    \"\"\"Authorization error\"\"\"
    pass


class DatabaseError(AppException):
    \"\"\"Database error\"\"\"
    pass


class CacheError(AppException):
    \"\"\"Cache error\"\"\"
    pass


class ExternalServiceError(AppException):
    \"\"\"External service error\"\"\"
    pass
""")
    
    # 创建API模块
    api_dir = project_dir / "api"
    api_dir.mkdir(exist_ok=True)
    (api_dir / "__init__.py").write_text("\"\"\"API module\"\"\"")
    
    (api_dir / "app.py").write_text("""\"\"\"
Main application API
\"\"\"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    UserService, ProductService, OrderService,
    User, Product, Order,
    ValidationError, NotFoundError, AuthenticationError,
    Logger
)


def main():
    \"\"\"Main function\"\"\"
    logger = Logger("Application")
    logger.info("Starting application")
    
    # Initialize services
    user_service = UserService()
    product_service = ProductService()
    order_service = OrderService(user_service, product_service)
    
    # Create some test data
    logger.info("Creating test data")
    
    # Create users
    user1 = user_service.create("alice", "alice@example.com", "password123")
    user2 = user_service.create("bob", "bob@example.com", "password456")
    user3 = user_service.create("charlie", "charlie@example.com", "password789")
    
    # Create products
    product1 = product_service.create(
        "Laptop", "High-performance laptop", 999.99, 50, "Electronics", ["tech", "laptop"]
    )
    product2 = product_service.create(
        "Mouse", "Wireless mouse", 29.99, 200, "Accessories", ["tech", "accessory"]
    )
    product3 = product_service.create(
        "Keyboard", "Mechanical keyboard", 149.99, 100, "Accessories", ["tech", "accessory"]
    )
    product4 = product_service.create(
        "Monitor", "27\" 4K monitor", 399.99, 30, "Electronics", ["tech", "monitor"]
    )
    
    # Create orders
    order1 = order_service.create(
        user1.id,
        [
            {"product_id": product1.id, "quantity": 1},
            {"product_id": product2.id, "quantity": 2}
        ]
    )
    
    order2 = order_service.create(
        user2.id,
        [
            {"product_id": product3.id, "quantity": 1},
            {"product_id": product4.id, "quantity": 1}
        ]
    )
    
    # Update order statuses
    order_service.update_status(order1.id, "processing")
    order_service.update_status(order2.id, "shipped")
    
    # Print results
    logger.info("\\n=== Application Started ===")
    logger.info(f"Users created: {len(user_service.get_all())}")
    logger.info(f"Products created: {len(product_service.search(''))}")
    logger.info(f"Orders created: {len(order_service.get_by_user(user1.id)) + len(order_service.get_by_user(user2.id))}")
    
    # Search functionality
    logger.info("\\n=== Search Results ===")
    search_results = product_service.search("tech")
    logger.info(f"Products matching 'tech': {len(search_results)}")
    
    logger.info("Application running successfully!")


if __name__ == "__main__":
    main()
""")
    
    # 创建更多子模块
    (project_dir / "cli.py").write_text("""#!/usr/bin/env python3
\"\"\"
CLI interface
\"\"\"
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core import UserService, ProductService, OrderService, Logger


def list_users(args):
    \"\"\"List all users\"\"\"
    service = UserService()
    users = service.get_all()
    print(f\"Users ({len(users)}):\")
    for user in users:
        print(f\"  - {user.username} ({user.email})\")


def create_user(args):
    \"\"\"Create a new user\"\"\"
    service = UserService()
    user = service.create(args.username, args.email, args.password)
    print(f\"Created user: {user.username} with ID {user.id}\")


def main():
    \"\"\"Main CLI function\"\"\"
    parser = argparse.ArgumentParser(description=\"Application CLI\")
    subparsers = parser.add_subparsers(dest=\"command\")
    
    # User commands
    user_parser = subparsers.add_parser(\"users\", help=\"User management\")
    user_subparsers = user_parser.add_subparsers(dest=\"user_command\")
    
    list_parser = user_subparsers.add_parser(\"list\", help=\"List users\")
    list_parser.set_defaults(func=list_users)
    
    create_parser = user_subparsers.add_parser(\"create\", help=\"Create user\")
    create_parser.add_argument(\"username\")
    create_parser.add_argument(\"email\")
    create_parser.add_argument(\"password\")
    create_parser.set_defaults(func=create_user)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == \"__main__\":
    main()
""")


def create_javascript_test_project(base_path: Path):
    """创建复杂的JavaScript/TypeScript测试项目"""
    js_dir = base_path / "javascript_project"
    js_dir.mkdir(exist_ok=True, parents=True)
    
    (js_dir / "package.json").write_text('''{
  "name": "test-app",
  "version": "1.0.0",
  "description": "Test JavaScript Application",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "build": "webpack --mode production",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.0",
    "axios": "^1.4.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "webpack": "^5.0.0"
  }
}''')
    
    src_dir = js_dir / "src"
    src_dir.mkdir(exist_ok=True, parents=True)
    (src_dir / "utils").mkdir(exist_ok=True, parents=True)
    (src_dir / "services").mkdir(exist_ok=True, parents=True)
    (src_dir / "routes").mkdir(exist_ok=True, parents=True)
    (src_dir / "tests").mkdir(exist_ok=True, parents=True)
    
    (src_dir / "index.js").write_text('''/**
 * Main application entry point
 */
const express = require('express');
const bodyParser = require('body-parser');
const logger = require('./utils/logger');
const userRouter = require('./routes/users');
const productRouter = require('./routes/products');
const orderRouter = require('./routes/orders');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/api/users', userRouter);
app.use('/api/products', productRouter);
app.use('/api/orders', orderRouter);

app.get('/', (req, res) => {
  res.json({
    name: 'Test Application',
    version: '1.0.0',
    status: 'running'
  });
});

app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
});

module.exports = app;
''')
    
    (src_dir / "utils" / "logger.js").write_text('''/**
 * Logger utility
 */
const timestamp = () => new Date().toISOString();

const log = (level, message) => {
  console.log(`[${timestamp()}] [${level}] ${message}`);
};

module.exports = {
  info: (msg) => log('INFO', msg),
  warn: (msg) => log('WARN', msg),
  error: (msg) => log('ERROR', msg),
  debug: (msg) => log('DEBUG', msg)
};
''')
    
    (src_dir / "utils" / "validators.js").write_text('''/**
 * Validation utilities
 */

function validateEmail(email) {
  const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return re.test(email);
}

function validatePrice(price) {
  return typeof price === 'number' && price >= 0;
}

function validatePassword(password) {
  return password && password.length >= 8;
}

function validateRequired(value) {
  return value !== null && value !== undefined && value !== '';
}

module.exports = {
  validateEmail,
  validatePrice,
  validatePassword,
  validateRequired
};
''')
    
    (src_dir / "services" / "userService.js").write_text('''/**
 * User service
 */
const { validateEmail, validatePassword, validateRequired } = require('../utils/validators');
const logger = require('../utils/logger');

class UserService {
  constructor() {
    this.users = new Map();
    this.nextId = 1;
  }
  
  createUser(userData) {
    if (!validateEmail(userData.email)) {
      throw new Error('Invalid email');
    }
    
    if (!validatePassword(userData.password)) {
      throw new Error('Password too short');
    }
    
    const user = {
      id: this.nextId++,
      username: userData.username,
      email: userData.email,
      password: this._hashPassword(userData.password),
      isActive: true,
      roles: userData.roles || ['user'],
      createdAt: new Date().toISOString()
    };
    
    this.users.set(user.id, user);
    logger.info(`Created user: ${user.username}`);
    return user;
  }
  
  getUserById(id) {
    const user = this.users.get(Number(id));
    if (!user) {
      throw new Error('User not found');
    }
    return user;
  }
  
  getAllUsers() {
    return Array.from(this.users.values());
  }
  
  updateUser(id, updateData) {
    const user = this.getUserById(id);
    Object.assign(user, updateData, { updatedAt: new Date().toISOString() });
    logger.info(`Updated user: ${id}`);
    return user;
  }
  
  deleteUser(id) {
    if (!this.users.delete(Number(id))) {
      throw new Error('User not found');
    }
    logger.info(`Deleted user: ${id}`);
  }
  
  _hashPassword(password) {
    // Simple hash (not for production)
    return require('crypto').createHash('sha256').update(password).digest('hex');
  }
  
  authenticate(username, password) {
    const hashedPassword = this._hashPassword(password);
    for (const user of this.users.values()) {
      if (user.username === username && user.password === hashedPassword) {
        return user;
      }
    }
    throw new Error('Invalid credentials');
  }
}

module.exports = UserService;
''')
    
    (src_dir / "services" / "productService.js").write_text('''/**
 * Product service
 */
const { validatePrice, validateRequired } = require('../utils/validators');
const logger = require('../utils/logger');

class ProductService {
  constructor() {
    this.products = new Map();
    this.nextId = 1;
  }
  
  createProduct(productData) {
    if (!validateRequired(productData.name)) {
      throw new Error('Name is required');
    }
    
    if (!validatePrice(productData.price)) {
      throw new Error('Invalid price');
    }
    
    const product = {
      id: this.nextId++,
      name: productData.name,
      description: productData.description || '',
      price: productData.price,
      stock: productData.stock || 0,
      category: productData.category || 'default',
      tags: productData.tags || [],
      createdAt: new Date().toISOString()
    };
    
    this.products.set(product.id, product);
    logger.info(`Created product: ${product.name}`);
    return product;
  }
  
  getProductById(id) {
    const product = this.products.get(Number(id));
    if (!product) {
      throw new Error('Product not found');
    }
    return product;
  }
  
  getAllProducts() {
    return Array.from(this.products.values());
  }
  
  searchProducts(query) {
    const lowerQuery = query.toLowerCase();
    return Array.from(this.products.values()).filter(product => 
      product.name.toLowerCase().includes(lowerQuery) ||
      product.description.toLowerCase().includes(lowerQuery) ||
      product.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    );
  }
  
  updateProduct(id, updateData) {
    const product = this.getProductById(id);
    Object.assign(product, updateData, { updatedAt: new Date().toISOString() });
    logger.info(`Updated product: ${id}`);
    return product;
  }
  
  deleteProduct(id) {
    if (!this.products.delete(Number(id))) {
      throw new Error('Product not found');
    }
    logger.info(`Deleted product: ${id}`);
  }
  
  updateStock(id, quantity) {
    const product = this.getProductById(id);
    if (product.stock + quantity < 0) {
      throw new Error('Insufficient stock');
    }
    product.stock += quantity;
    return product;
  }
}

module.exports = ProductService;
''')
    
    (src_dir / "services" / "orderService.js").write_text('''/**
 * Order service
 */
const logger = require('../utils/logger');

class OrderService {
  constructor(userService, productService) {
    this.userService = userService;
    this.productService = productService;
    this.orders = new Map();
    this.nextId = 1;
  }
  
  createOrder(userId, items) {
    // Validate user
    this.userService.getUserById(userId);
    
    let totalAmount = 0;
    const orderItems = [];
    
    for (const itemData of items) {
      const product = this.productService.getProductById(itemData.productId);
      
      if (product.stock < itemData.quantity) {
        throw new Error(`Insufficient stock for ${product.name}`);
      }
      
      const orderItem = {
        productId: product.id,
        product,
        quantity: itemData.quantity,
        unitPrice: product.price,
        subtotal: product.price * itemData.quantity
      };
      
      orderItems.push(orderItem);
      totalAmount += orderItem.subtotal;
    }
    
    const order = {
      id: this.nextId++,
      userId,
      items: orderItems,
      totalAmount,
      status: 'pending',
      createdAt: new Date().toISOString()
    };
    
    this.orders.set(order.id, order);
    
    // Update stock
    for (const item of orderItems) {
      this.productService.updateStock(item.productId, -item.quantity);
    }
    
    logger.info(`Created order: ${order.id}`);
    return order;
  }
  
  getOrderById(id) {
    const order = this.orders.get(Number(id));
    if (!order) {
      throw new Error('Order not found');
    }
    return order;
  }
  
  getOrdersByUser(userId) {
    return Array.from(this.orders.values()).filter(order => order.userId === userId);
  }
  
  updateOrderStatus(id, status) {
    const order = this.getOrderById(id);
    const validStatuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];
    if (!validStatuses.includes(status)) {
      throw new Error('Invalid status');
    }
    order.status = status;
    order.updatedAt = new Date().toISOString();
    logger.info(`Updated order ${id} status to ${status}`);
    return order;
  }
}

module.exports = OrderService;
''')
    
    (src_dir / "routes" / "users.js").write_text('''/**
 * User routes
 */
const express = require('express');
const router = express.Router();
const UserService = require('../services/userService');
const logger = require('../utils/logger');

const userService = new UserService();

router.get('/', (req, res) => {
  try {
    const users = userService.getAllUsers();
    res.json({ success: true, data: users });
  } catch (error) {
    logger.error(`Error getting users: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/:id', (req, res) => {
  try {
    const user = userService.getUserById(req.params.id);
    res.json({ success: true, data: user });
  } catch (error) {
    logger.error(`Error getting user: ${error.message}`);
    res.status(404).json({ success: false, error: error.message });
  }
});

router.post('/', (req, res) => {
  try {
    const user = userService.createUser(req.body);
    res.status(201).json({ success: true, data: user });
  } catch (error) {
    logger.error(`Error creating user: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

router.put('/:id', (req, res) => {
  try {
    const user = userService.updateUser(req.params.id, req.body);
    res.json({ success: true, data: user });
  } catch (error) {
    logger.error(`Error updating user: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

router.delete('/:id', (req, res) => {
  try {
    userService.deleteUser(req.params.id);
    res.json({ success: true });
  } catch (error) {
    logger.error(`Error deleting user: ${error.message}`);
    res.status(404).json({ success: false, error: error.message });
  }
});

module.exports = router;
''')
    
    (src_dir / "routes" / "products.js").write_text('''/**
 * Product routes
 */
const express = require('express');
const router = express.Router();
const ProductService = require('../services/productService');
const logger = require('../utils/logger');

const productService = new ProductService();

router.get('/', (req, res) => {
  try {
    const products = productService.getAllProducts();
    res.json({ success: true, data: products });
  } catch (error) {
    logger.error(`Error getting products: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/search', (req, res) => {
  try {
    const products = productService.searchProducts(req.query.q || '');
    res.json({ success: true, data: products });
  } catch (error) {
    logger.error(`Error searching products: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/:id', (req, res) => {
  try {
    const product = productService.getProductById(req.params.id);
    res.json({ success: true, data: product });
  } catch (error) {
    logger.error(`Error getting product: ${error.message}`);
    res.status(404).json({ success: false, error: error.message });
  }
});

router.post('/', (req, res) => {
  try {
    const product = productService.createProduct(req.body);
    res.status(201).json({ success: true, data: product });
  } catch (error) {
    logger.error(`Error creating product: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

module.exports = router;
''')
    
    (src_dir / "routes" / "orders.js").write_text('''/**
 * Order routes
 */
const express = require('express');
const router = express.Router();
const UserService = require('../services/userService');
const ProductService = require('../services/productService');
const OrderService = require('../services/orderService');
const logger = require('../utils/logger');

const userService = new UserService();
const productService = new ProductService();
const orderService = new OrderService(userService, productService);

router.post('/', (req, res) => {
  try {
    const order = orderService.createOrder(req.body.userId, req.body.items);
    res.status(201).json({ success: true, data: order });
  } catch (error) {
    logger.error(`Error creating order: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

router.get('/:id', (req, res) => {
  try {
    const order = orderService.getOrderById(req.params.id);
    res.json({ success: true, data: order });
  } catch (error) {
    logger.error(`Error getting order: ${error.message}`);
    res.status(404).json({ success: false, error: error.message });
  }
});

router.put('/:id/status', (req, res) => {
  try {
    const order = orderService.updateOrderStatus(req.params.id, req.body.status);
    res.json({ success: true, data: order });
  } catch (error) {
    logger.error(`Error updating order status: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

module.exports = router;
''')
    
    (src_dir / "tests" / "userService.test.js").write_text('''/**
 * Tests for user service
 */
const UserService = require('../services/userService');

describe('UserService', () => {
  let service;
  
  beforeEach(() => {
    service = new UserService();
  });
  
  test('should create user', () => {
    const user = service.createUser({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123'
    });
    
    expect(user.id).toBeDefined();
    expect(user.username).toBe('testuser');
    expect(user.email).toBe('test@example.com');
  });
  
  test('should get user by id', () => {
    const user = service.createUser({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123'
    });
    
    const foundUser = service.getUserById(user.id);
    expect(foundUser.username).toBe('testuser');
  });
  
  test('should throw error for invalid email', () => {
    expect(() => {
      service.createUser({
        username: 'testuser',
        email: 'invalid-email',
        password: 'password123'
      });
    }).toThrow();
  });
});
''')


def create_go_test_project(base_path: Path):
    """创建复杂的Go测试项目"""
    go_dir = base_path / "go_project"
    go_dir.mkdir(exist_ok=True, parents=True)
    
    (go_dir / "go.mod").write_text('''module test-go-app

go 1.21
''')
    
    src_dir = go_dir / "internal"
    src_dir.mkdir(exist_ok=True, parents=True)
    (src_dir / "models").mkdir(exist_ok=True, parents=True)
    (src_dir / "services").mkdir(exist_ok=True, parents=True)
    
    (src_dir / "models" / "user.go").write_text('''package models

import "time"

// User represents a user in the system
type User struct {
    ID        int       `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    Password  string    `json:"-"`
    IsActive  bool      `json:"is_active"`
    Roles     []string  `json:"roles"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at,omitempty"`
}

// NewUser creates a new user
func NewUser(username, email, password string) *User {
    return &User{
        Username:  username,
        Email:     email,
        Password:  hashPassword(password),
        IsActive:  true,
        Roles:     []string{"user"},
        CreatedAt: time.Now(),
    }
}

func hashPassword(password string) string {
    return password // Simplified for test
}
''')
    
    (src_dir / "models" / "product.go").write_text('''package models

import "time"

// Product represents a product in the system
type Product struct {
    ID          int       `json:"id"`
    Name        string    `json:"name"`
    Description string    `json:"description"`
    Price       float64   `json:"price"`
    Stock       int       `json:"stock"`
    Category    string    `json:"category"`
    Tags        []string  `json:"tags"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at,omitempty"`
}

// NewProduct creates a new product
func NewProduct(name, description string, price float64, stock int, category string, tags []string) *Product {
    return &Product{
        Name:        name,
        Description: description,
        Price:       price,
        Stock:       stock,
        Category:    category,
        Tags:        tags,
        CreatedAt:   time.Now(),
    }
}
''')
    
    (src_dir / "models" / "order.go").write_text('''package models

import "time"

// OrderItem represents an item in an order
type OrderItem struct {
    ProductID int     `json:"product_id"`
    Quantity  int     `json:"quantity"`
    UnitPrice float64 `json:"unit_price"`
}

// Order represents an order in the system
type Order struct {
    ID          int         `json:"id"`
    UserID      int         `json:"user_id"`
    Items       []OrderItem `json:"items"`
    TotalAmount float64     `json:"total_amount"`
    Status      string      `json:"status"`
    CreatedAt   time.Time   `json:"created_at"`
    UpdatedAt   time.Time   `json:"updated_at,omitempty"`
}

// NewOrder creates a new order
func NewOrder(userID int, items []OrderItem, totalAmount float64) *Order {
    return &Order{
        UserID:      userID,
        Items:       items,
        TotalAmount: totalAmount,
        Status:      "pending",
        CreatedAt:   time.Now(),
    }
}
''')
    
    (src_dir / "services" / "userService.go").write_text('''package services

import (
    "errors"
    "fmt"
    "sync"
    "test-go-app/internal/models"
)

// UserService handles user operations
type UserService struct {
    users  map[int]*models.User
    nextID int
    mu     sync.RWMutex
}

// NewUserService creates a new UserService
func NewUserService() *UserService {
    return &UserService{
        users:  make(map[int]*models.User),
        nextID: 1,
    }
}

// Create creates a new user
func (s *UserService) Create(username, email, password string) (*models.User, error) {
    if username == "" || email == "" || password == "" {
        return nil, errors.New("username, email, and password are required")
    }
    
    s.mu.Lock()
    defer s.mu.Unlock()
    
    user := models.NewUser(username, email, password)
    user.ID = s.nextID
    s.nextID++
    s.users[user.ID] = user
    
    fmt.Printf("Created user: %s\\n", username)
    return user, nil
}

// GetByID gets a user by ID
func (s *UserService) GetByID(id int) (*models.User, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    user, exists := s.users[id]
    if !exists {
        return nil, errors.New("user not found")
    }
    return user, nil
}

// GetAll gets all users
func (s *UserService) GetAll() []*models.User {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    users := make([]*models.User, 0, len(s.users))
    for _, user := range s.users {
        users = append(users, user)
    }
    return users
}

// Update updates a user
func (s *UserService) Update(id int, username, email *string, isActive *bool) (*models.User, error) {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    user, exists := s.users[id]
    if !exists {
        return nil, errors.New("user not found")
    }
    
    if username != nil {
        user.Username = *username
    }
    if email != nil {
        user.Email = *email
    }
    if isActive != nil {
        user.IsActive = *isActive
    }
    
    return user, nil
}

// Delete deletes a user
func (s *UserService) Delete(id int) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    if _, exists := s.users[id]; !exists {
        return errors.New("user not found")
    }
    delete(s.users, id)
    return nil
}
''')
    
    (src_dir / "services" / "productService.go").write_text('''package services

import (
    "errors"
    "fmt"
    "strings"
    "sync"
    "test-go-app/internal/models"
)

// ProductService handles product operations
type ProductService struct {
    products map[int]*models.Product
    nextID   int
    mu       sync.RWMutex
}

// NewProductService creates a new ProductService
func NewProductService() *ProductService {
    return &ProductService{
        products: make(map[int]*models.Product),
        nextID:   1,
    }
}

// Create creates a new product
func (s *ProductService) Create(name, description string, price float64, stock int, category string, tags []string) (*models.Product, error) {
    if name == "" {
        return nil, errors.New("name is required")
    }
    if price < 0 {
        return nil, errors.New("price cannot be negative")
    }
    
    s.mu.Lock()
    defer s.mu.Unlock()
    
    product := models.NewProduct(name, description, price, stock, category, tags)
    product.ID = s.nextID
    s.nextID++
    s.products[product.ID] = product
    
    fmt.Printf("Created product: %s\\n", name)
    return product, nil
}

// GetByID gets a product by ID
func (s *ProductService) GetByID(id int) (*models.Product, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    product, exists := s.products[id]
    if !exists {
        return nil, errors.New("product not found")
    }
    return product, nil
}

// Search searches products
func (s *ProductService) Search(query string) []*models.Product {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    queryLower := strings.ToLower(query)
    results := make([]*models.Product, 0)
    
    for _, product := range s.products {
        if strings.Contains(strings.ToLower(product.Name), queryLower) ||
            strings.Contains(strings.ToLower(product.Description), queryLower) {
            results = append(results, product)
            continue
        }
        for _, tag := range product.Tags {
            if strings.Contains(strings.ToLower(tag), queryLower) {
                results = append(results, product)
                break
            }
        }
    }
    return results
}

// UpdateStock updates product stock
func (s *ProductService) UpdateStock(id int, quantity int) (*models.Product, error) {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    product, exists := s.products[id]
    if !exists {
        return nil, errors.New("product not found")
    }
    
    if product.Stock+quantity < 0 {
        return nil, errors.New("insufficient stock")
    }
    
    product.Stock += quantity
    return product, nil
}
''')
    
    (src_dir / "services" / "orderService.go").write_text('''package services

import (
    "errors"
    "fmt"
    "sync"
    "test-go-app/internal/models"
)

// OrderService handles order operations
type OrderService struct {
    userService    *UserService
    productService *ProductService
    orders         map[int]*models.Order
    nextID         int
    mu             sync.RWMutex
}

// NewOrderService creates a new OrderService
func NewOrderService(userService *UserService, productService *ProductService) *OrderService {
    return &OrderService{
        userService:    userService,
        productService: productService,
        orders:         make(map[int]*models.Order),
        nextID:         1,
    }
}

// Create creates a new order
func (s *OrderService) Create(userID int, items []models.OrderItem) (*models.Order, error) {
    // Validate user
    if _, err := s.userService.GetByID(userID); err != nil {
        return nil, err
    }
    
    var totalAmount float64
    var orderItems []models.OrderItem
    
    for _, item := range items {
        product, err := s.productService.GetByID(item.ProductID)
        if err != nil {
            return nil, err
        }
        
        if product.Stock < item.Quantity {
            return nil, errors.New("insufficient stock")
        }
        
        subtotal := float64(item.Quantity) * product.Price
        totalAmount += subtotal
        
        orderItems = append(orderItems, models.OrderItem{
            ProductID: item.ProductID,
            Quantity:  item.Quantity,
            UnitPrice: product.Price,
        })
    }
    
    s.mu.Lock()
    defer s.mu.Unlock()
    
    order := models.NewOrder(userID, orderItems, totalAmount)
    order.ID = s.nextID
    s.nextID++
    s.orders[order.ID] = order
    
    // Update stock
    for _, item := range orderItems {
        s.productService.UpdateStock(item.ProductID, -item.Quantity)
    }
    
    fmt.Printf("Created order: %d\\n", order.ID)
    return order, nil
}

// GetByID gets an order by ID
func (s *OrderService) GetByID(id int) (*models.Order, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    order, exists := s.orders[id]
    if !exists {
        return nil, errors.New("order not found")
    }
    return order, nil
}

// UpdateStatus updates order status
func (s *OrderService) UpdateStatus(id int, status string) (*models.Order, error) {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    order, exists := s.orders[id]
    if !exists {
        return nil, errors.New("order not found")
    }
    
    validStatuses := map[string]bool{
        "pending":    true,
        "processing": true,
        "shipped":    true,
        "delivered":  true,
        "cancelled":  true,
    }
    
    if !validStatuses[status] {
        return nil, errors.New("invalid status")
    }
    
    order.Status = status
    return order, nil
}
''')
    
    (go_dir / "main.go").write_text('''package main

import (
    "fmt"
    "test-go-app/internal/services"
    "test-go-app/internal/models"
)

func main() {
    fmt.Println("Go Test Application")
    fmt.Println("====================")
    
    // Initialize services
    userService := services.NewUserService()
    productService := services.NewProductService()
    orderService := services.NewOrderService(userService, productService)
    
    // Create test data
    user1, _ := userService.Create("alice", "alice@example.com", "password123")
    user2, _ := userService.Create("bob", "bob@example.com", "password456")
    
    product1, _ := productService.Create("Laptop", "High-performance laptop", 999.99, 50, "Electronics", []string{"tech"})
    product2, _ := productService.Create("Mouse", "Wireless mouse", 29.99, 200, "Accessories", []string{"tech"})
    product3, _ := productService.Create("Keyboard", "Mechanical keyboard", 149.99, 100, "Accessories", []string{"tech"})
    
    order1, _ := orderService.Create(user1.ID, []models.OrderItem{
        {ProductID: product1.ID, Quantity: 1},
        {ProductID: product2.ID, Quantity: 2},
    })
    
    order2, _ := orderService.Create(user2.ID, []models.OrderItem{
        {ProductID: product3.ID, Quantity: 1},
    })
    
    orderService.UpdateStatus(order1.ID, "processing")
    
    fmt.Printf("\\nUsers: %d\\n", len(userService.GetAll()))
    fmt.Printf("Products: %d\\n", len(productService.Search("")))
    fmt.Printf("Orders: 2\\n")
    fmt.Println("\\nApplication running successfully!")
}
''')


def main():
    """主函数 - 创建大规模复杂测试项目"""
    base_path = Path(__file__).parent / "large_test_project"
    
    print("Creating large-scale complex test project...")
    
    create_python_test_project(base_path)
    print("✓ Python project created")
    
    create_javascript_test_project(base_path)
    print("✓ JavaScript/TypeScript project created")
    
    create_go_test_project(base_path)
    print("✓ Go project created")
    
    # 创建README
    (base_path / "README.md").write_text("""# Large-Scale Test Project

这是一个用于深度测试代码知识图谱系统的大规模复杂测试项目，包含多种语言的代码库。

## 项目结构

```
large_test_project/
├── python_project/      # Python项目 (复杂模块化架构)
│   ├── core/            # 核心模块
│   ├── api/             # API模块
│   └── cli.py
├── javascript_project/  # JavaScript/Node.js项目 (Express应用)
│   ├── src/
│   │   ├── services/    # 服务层
│   │   ├── routes/      # 路由层
│   │   ├── utils/       # 工具函数
│   │   └── tests/       # 测试文件
│   └── package.json
└── go_project/          # Go项目 (模块化架构)
    ├── internal/
    │   ├── models/      # 模型
    │   └── services/    # 服务
    └── main.go
```

## 功能特性

- 多语言支持 (Python, JavaScript, Go)
- 复杂的模块依赖关系
- 丰富的函数调用
- 完整的业务逻辑
""")
    
    print(f"\n✓ Complete! Test project created at: {base_path}")
    print("Ready for deep testing!")


if __name__ == "__main__":
    main()
