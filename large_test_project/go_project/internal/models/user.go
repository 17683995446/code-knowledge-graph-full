package models

import "time"

// User represents a user in the system
type User struct {
    ID        int       `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    Password  string    `json:"-"`
    IsActive  bool      `json:"is_active"`
    Roles     []string  `json:"roles"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at,omitempty"`
}

// NewUser creates a new user
func NewUser(username, email, password string) *User {
    return &User{
        Username:  username,
        Email:     email,
        Password:  hashPassword(password),
        IsActive:  true,
        Roles:     []string{"user"},
        CreatedAt: time.Now(),
    }
}

func hashPassword(password string) string {
    return password // Simplified for test
}
