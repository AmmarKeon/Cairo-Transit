/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#fffaf0',
        'surface-soft': '#faf5e8',
        'surface-card': '#f5f0e0',
        ink: '#0a0a0a',
        body: '#3a3a3a',
        muted: '#6a6a6a',
        'brand-pink': '#ff4d8b',
        'brand-teal': '#1a3a3a',
        'brand-lavender': '#b8a4ed',
        'brand-peach': '#ffb084',
        'brand-ochre': '#e8b94a',
        'brand-mint': '#a4d4c5',
        'hairline': '#e5e5e5',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'card': 'rgba(0,0,0,0.04) 0px 4px 18px, rgba(0,0,0,0.027) 0px 2.025px 7.84688px, rgba(0,0,0,0.02) 0px 0.8px 2.925px, rgba(0,0,0,0.01) 0px 0.175px 1.04062px',
      },
      borderRadius: {
        'xl': '12px',
      },
    },
  },
  plugins: [],
}