package models

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
