package services

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
    
    fmt.Printf("Created product: %s\n", name)
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
