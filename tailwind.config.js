/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // <-- enables class-based dark mode

  content: [
    "./lms/**/*.html",
    "./lms/**/**/*.html",
    "./templates/**/*.html",
    "./static/**/*.js",
    "./**/*.py",
  ],

  theme: {
    extend: {
      fontFamily: {
        barriecito: ['Barriecito', 'cursive'],
      },
    },
  },

  plugins: [require('@tailwindcss/line-clamp')],

};
