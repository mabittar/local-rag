/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        surface: '#1e293b',
        'surface-hover': '#334155',
        primary: '#3b82f6',
        'primary-hover': '#2563eb',
        secondary: '#64748b',
        text: '#f1f5f9',
        'text-muted': '#94a3b8',
        border: '#334155',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
