/**
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
