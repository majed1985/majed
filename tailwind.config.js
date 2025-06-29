/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js'
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Tajawal', 'Arial', 'sans-serif'],
      },
      colors: {
        'blue-dark': '#072c52',
        'blue-light': '#118bff',
        accent: '#009c58',
      },
    },
  },
  plugins: [],
}
