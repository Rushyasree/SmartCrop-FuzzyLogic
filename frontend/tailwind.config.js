export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#2D5016',
        secondary: '#6B8E23',
        accent: '#FFA500',
        success: '#10B981',
        danger: '#EF4444',
        warning: '#F59E0B',
        light: '#F3F4F6',
        dark: '#1F2937'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
}
