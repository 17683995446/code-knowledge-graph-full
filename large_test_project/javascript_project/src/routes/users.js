/**
 * User routes
 */
const express = require('express');
const router = express.Router();
const UserService = require('../services/userService');
const logger = require('../utils/logger');

const userService = new UserService();

router.get('/', (req, res) => {
  try {
    const users = userService.getAllUsers();
    res.json({ success: true, data: users });
  } catch (error) {
    logger.error(`Error getting users: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
});

router.get('/:id', (req, res) => {
  try {
    const user = userService.getUserById(req.params.id);
    res.json({ success: true, data: user });
  } catch (error) {
    logger.error(`Error getting user: ${error.message}`);
    res.status(404).json({ success: false, error: error.message });
  }
});

router.post('/', (req, res) => {
  try {
    const user = userService.createUser(req.body);
    res.status(201).json({ success: true, data: user });
  } catch (error) {
    logger.error(`Error creating user: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

router.put('/:id', (req, res) => {
  try {
    const user = userService.updateUser(req.params.id, req.body);
    res.json({ success: true, data: user });
  } catch (error) {
    logger.error(`Error updating user: ${error.message}`);
    res.status(400).json({ success: false, error: error.message });
  }
});

router.delete('/:id', (req, res) => {
  try {
    userService.deleteUser(req.params.id);
    res.json({ success: true });
  } catch (error) {
    logger.error(`Error deleting user: ${error.message}`);
    res.status(404).json({ success: false, error: error.message });
  }
});

module.exports = router;
