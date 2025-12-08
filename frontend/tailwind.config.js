/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        lightsaber: {
          blue: '#4A9EFF',
          green: '#7FFF00',
          red: '#FF3B3B',
          purple: '#B270FF',
          yellow: '#FFE66D',
          orange: '#FF8C42',
        },
        space: {
          dark: '#0A0E27',
          darker: '#050813',
          accent: '#1A1F3A',
        }
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-glow': 'pulse-glow 1.5s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { filter: 'drop-shadow(0 0 5px currentColor)' },
          '100%': { filter: 'drop-shadow(0 0 20px currentColor)' },
        },
        'pulse-glow': {
          '0%, 100%': { filter: 'drop-shadow(0 0 8px currentColor)', opacity: '1' },
          '50%': { filter: 'drop-shadow(0 0 15px currentColor)', opacity: '0.8' },
        }
      }
    },
  },
  plugins: [],
}
