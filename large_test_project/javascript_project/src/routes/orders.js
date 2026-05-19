/**
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
