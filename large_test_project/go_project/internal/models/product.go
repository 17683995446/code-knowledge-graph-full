package models

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
