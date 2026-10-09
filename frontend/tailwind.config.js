/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        porcelain: "#F8F7F4",
        'signal-blue': "#0057FF",
        signalBlue: "#0057FF",
        cpcb: {
          good: "#16a34a",
          satisfactory: "#84cc16",
          moderate: "#eab308",
          poor: "#f97316",
          veryPoor: "#ef4444",
          severe: "#991b1b",
        },
      },
    },
  },
  plugins: [],
}
