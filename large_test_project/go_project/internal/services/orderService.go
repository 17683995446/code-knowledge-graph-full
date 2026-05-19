package services

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
    
    fmt.Printf("Created order: %d\n", order.ID)
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
