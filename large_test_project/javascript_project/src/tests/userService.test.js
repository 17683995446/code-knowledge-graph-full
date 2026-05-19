/**
 * Tests for user service
 */
const UserService = require('../services/userService');

describe('UserService', () => {
  let service;
  
  beforeEach(() => {
    service = new UserService();
  });
  
  test('should create user', () => {
    const user = service.createUser({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123'
    });
    
    expect(user.id).toBeDefined();
    expect(user.username).toBe('testuser');
    expect(user.email).toBe('test@example.com');
  });
  
  test('should get user by id', () => {
    const user = service.createUser({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123'
    });
    
    const foundUser = service.getUserById(user.id);
    expect(foundUser.username).toBe('testuser');
  });
  
  test('should throw error for invalid email', () => {
    expect(() => {
      service.createUser({
        username: 'testuser',
        email: 'invalid-email',
        password: 'password123'
      });
    }).toThrow();
  });
});
