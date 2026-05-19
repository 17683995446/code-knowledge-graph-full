/**
 * Logger utility
 */
const timestamp = () => new Date().toISOString();

const log = (level, message) => {
  console.log(`[${timestamp()}] [${level}] ${message}`);
};

module.exports = {
  info: (msg) => log('INFO', msg),
  warn: (msg) => log('WARN', msg),
  error: (msg) => log('ERROR', msg),
  debug: (msg) => log('DEBUG', msg)
};
