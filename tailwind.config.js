/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,js}",
    "./apps/*/templates/**/*.{html,js}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1e3a8a', // Deep blue for navbar
        accent: '#f97316', // Orange
        background: '#ffffff', // White
      },
    },
  },
  plugins: [],
}