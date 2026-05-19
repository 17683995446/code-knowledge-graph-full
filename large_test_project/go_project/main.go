package main

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
    
    fmt.Printf("\nUsers: %d\n", len(userService.GetAll()))
    fmt.Printf("Products: %d\n", len(productService.Search("")))
    fmt.Printf("Orders: 2\n")
    fmt.Println("\nApplication running successfully!")
}
