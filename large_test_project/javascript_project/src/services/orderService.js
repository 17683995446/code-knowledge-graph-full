/**
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
