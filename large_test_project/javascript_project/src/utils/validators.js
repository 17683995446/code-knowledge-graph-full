/**
 * Validation utilities
 */

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePrice(price) {
  return typeof price === 'number' && price >= 0;
}

function validatePassword(password) {
  return password && password.length >= 8;
}

function validateRequired(value) {
  return value !== null && value !== undefined && value !== '';
}

module.exports = {
  validateEmail,
  validatePrice,
  validatePassword,
  validateRequired
};
