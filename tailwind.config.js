// ...existing code...
export const content = [
    './lms/**/*.html',
    './lms/**/**/*.html',
    './**/*.py',
    './templates/**/*.html',
    // add paths that match your template locations
];

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        barriecito: ['Barriecito', 'cursive'],
      },
    },
  },
  plugins: [],
}
