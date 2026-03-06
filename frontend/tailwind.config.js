/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        body: ['Outfit', 'sans-serif'],
      },
      colors: {
        ink: "#050505",
        "cyber-cyan": "#00F0FF",
        "acid-lime": "#CFFF04",
        "cyber-red": "#FF2E2E",
      }
    },
  },
  plugins: [],
}
