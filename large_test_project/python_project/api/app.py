"""
Main application API
"""
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
    """Main function"""
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
        "Monitor", "27" 4K monitor", 399.99, 30, "Electronics", ["tech", "monitor"]
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
    logger.info("\n=== Application Started ===")
    logger.info(f"Users created: {len(user_service.get_all())}")
    logger.info(f"Products created: {len(product_service.search(''))}")
    logger.info(f"Orders created: {len(order_service.get_by_user(user1.id)) + len(order_service.get_by_user(user2.id))}")
    
    # Search functionality
    logger.info("\n=== Search Results ===")
    search_results = product_service.search("tech")
    logger.info(f"Products matching 'tech': {len(search_results)}")
    
    logger.info("Application running successfully!")


if __name__ == "__main__":
    main()
