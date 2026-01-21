/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      spacing: {
        '144.5': '36.125rem',
        '288.75': '72.1875rem',
      },
      aspectRatio: {
        '1155/678': '1155 / 678',
      },
      backgroundImage: {
        'linear-to-tr': 'linear-gradient(to top right, var(--tw-gradient-stops))',
      },
      colors: {
        indigo: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
      },
    },
  },
  plugins: [],
}