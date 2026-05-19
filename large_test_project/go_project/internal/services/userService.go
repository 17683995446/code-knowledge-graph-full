package services

import (
    "errors"
    "fmt"
    "sync"
    "test-go-app/internal/models"
)

// UserService handles user operations
type UserService struct {
    users  map[int]*models.User
    nextID int
    mu     sync.RWMutex
}

// NewUserService creates a new UserService
func NewUserService() *UserService {
    return &UserService{
        users:  make(map[int]*models.User),
        nextID: 1,
    }
}

// Create creates a new user
func (s *UserService) Create(username, email, password string) (*models.User, error) {
    if username == "" || email == "" || password == "" {
        return nil, errors.New("username, email, and password are required")
    }
    
    s.mu.Lock()
    defer s.mu.Unlock()
    
    user := models.NewUser(username, email, password)
    user.ID = s.nextID
    s.nextID++
    s.users[user.ID] = user
    
    fmt.Printf("Created user: %s\n", username)
    return user, nil
}

// GetByID gets a user by ID
func (s *UserService) GetByID(id int) (*models.User, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    user, exists := s.users[id]
    if !exists {
        return nil, errors.New("user not found")
    }
    return user, nil
}

// GetAll gets all users
func (s *UserService) GetAll() []*models.User {
    s.mu.RLock()
    defer s.mu.RUnlock()
    
    users := make([]*models.User, 0, len(s.users))
    for _, user := range s.users {
        users = append(users, user)
    }
    return users
}

// Update updates a user
func (s *UserService) Update(id int, username, email *string, isActive *bool) (*models.User, error) {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    user, exists := s.users[id]
    if !exists {
        return nil, errors.New("user not found")
    }
    
    if username != nil {
        user.Username = *username
    }
    if email != nil {
        user.Email = *email
    }
    if isActive != nil {
        user.IsActive = *isActive
    }
    
    return user, nil
}

// Delete deletes a user
func (s *UserService) Delete(id int) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    if _, exists := s.users[id]; !exists {
        return errors.New("user not found")
    }
    delete(s.users, id)
    return nil
}
