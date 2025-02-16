import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Check if we are running in production (on the server)
const isProduction = process.env.NODE_ENV === "production";

// Set the base URL dynamically
export default defineConfig({
  plugins: [react()],
  base: isProduction ? "/~u045/weather-chat/" : "/",  // switch based on environment (run dev or run build)
});
