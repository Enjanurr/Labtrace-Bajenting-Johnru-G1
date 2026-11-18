/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./*/forms.py",
  ],
  theme: {
    extend: {
      boxShadow: {
        "soft-xs": "0 1px 2px 0 rgb(15 23 42 / 0.05)",
        "soft-sm": "0 2px 8px -2px rgb(15 23 42 / 0.08), 0 1px 3px 0 rgb(15 23 42 / 0.05)",
        "soft-xl": "0 20px 35px -12px rgb(15 23 42 / 0.16), 0 8px 14px -8px rgb(15 23 42 / 0.1)",
      },
    },
  },
  plugins: [],
};