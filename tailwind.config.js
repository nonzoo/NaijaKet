/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html', // Include template files in the main templates folder
    './core/templates/**/*.html', // Include template files in the core app's templates folder
    './store/templates/**/*.html', // Include template files in the store app's templates folder
    './userprofile/templates/**/*.html', // Include template files in the userprofile app's templates folder
    
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
