/**
 * User service
 */
const { validateEmail, validatePassword, validateRequired } = require('../utils/validators');
const logger = require('../utils/logger');

class UserService {
  constructor() {
    this.users = new Map();
    this.nextId = 1;
  }
  
  createUser(userData) {
    if (!validateEmail(userData.email)) {
      throw new Error('Invalid email');
    }
    
    if (!validatePassword(userData.password)) {
      throw new Error('Password too short');
    }
    
    const user = {
      id: this.nextId++,
      username: userData.username,
      email: userData.email,
      password: this._hashPassword(userData.password),
      isActive: true,
      roles: userData.roles || ['user'],
      createdAt: new Date().toISOString()
    };
    
    this.users.set(user.id, user);
    logger.info(`Created user: ${user.username}`);
    return user;
  }
  
  getUserById(id) {
    const user = this.users.get(Number(id));
    if (!user) {
      throw new Error('User not found');
    }
    return user;
  }
  
  getAllUsers() {
    return Array.from(this.users.values());
  }
  
  updateUser(id, updateData) {
    const user = this.getUserById(id);
    Object.assign(user, updateData, { updatedAt: new Date().toISOString() });
    logger.info(`Updated user: ${id}`);
    return user;
  }
  
  deleteUser(id) {
    if (!this.users.delete(Number(id))) {
      throw new Error('User not found');
    }
    logger.info(`Deleted user: ${id}`);
  }
  
  _hashPassword(password) {
    // Simple hash (not for production)
    return require('crypto').createHash('sha256').update(password).digest('hex');
  }
  
  authenticate(username, password) {
    const hashedPassword = this._hashPassword(password);
    for (const user of this.users.values()) {
      if (user.username === username && user.password === hashedPassword) {
        return user;
      }
    }
    throw new Error('Invalid credentials');
  }
}

module.exports = UserService;
