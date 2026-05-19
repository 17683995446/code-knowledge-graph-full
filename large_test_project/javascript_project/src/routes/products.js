/**
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
