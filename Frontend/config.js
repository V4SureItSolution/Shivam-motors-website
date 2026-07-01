// config.js

// Determine the environment based on the current hostname
const ENV = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
    ? 'development' 
    : 'production';

// Configuration settings for different environments
const CONFIG = {
    development: {
        // Local development URL
        API_BASE_URL: 'http://localhost:5000'
    },
    production: {
        // Production deployed server URL (placeholder, update when deploying)
        API_BASE_URL: 'https://your-production-backend-url.com' 
    }
};

// Global API Base URL variable for use in all frontend scripts
const API_BASE = CONFIG[ENV].API_BASE_URL;
