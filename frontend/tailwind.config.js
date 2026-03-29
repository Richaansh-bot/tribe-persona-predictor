/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neural': {
          50: '#e6fff9',
          100: '#b3fff0',
          200: '#80ffe6',
          300: '#4dffdc',
          400: '#1afdd3',
          500: '#00e6c3',
          600: '#00b899',
          700: '#008a70',
          800: '#005c46',
          900: '#002e23',
        },
        'cortex': {
          50: '#f0f7ff',
          100: '#e0efff',
          200: '#b3d9ff',
          300: '#80bfff',
          400: '#4d99ff',
          500: '#1a73e8',
          600: '#004dcc',
          700: '#003999',
          800: '#002666',
          900: '#001333',
        },
        'synapse': {
          50: '#fff5f5',
          100: '#ffe0e0',
          200: '#ffb3b3',
          300: '#ff8080',
          400: '#ff4d4d',
          500: '#ff3333',
          600: '#cc0000',
          700: '#990000',
          800: '#660000',
          900: '#330000',
        },
      },
      fontFamily: {
        'display': ['Space Grotesk', 'system-ui', 'sans-serif'],
        'body': ['Outfit', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'brain-wave': 'brain-wave 3s ease-in-out infinite',
        'synaptic': 'synaptic 1.5s ease-out forwards',
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'rotate-slow': 'rotate-slow 20s linear infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'brain-wave': {
          '0%, 100%': { strokeDashoffset: '1000', opacity: '0.3' },
          '50%': { strokeDashoffset: '0', opacity: '1' },
        },
        'synaptic': {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '50%': { transform: 'scale(1.2)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'rotate-slow': {
          'from': { transform: 'rotate(0deg)' },
          'to': { transform: 'rotate(360deg)' },
        },
      },
    },
  },
  plugins: [],
}
