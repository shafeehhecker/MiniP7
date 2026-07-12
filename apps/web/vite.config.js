var _a;
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Dev server proxies /api to the FastAPI backend (apps/api), so the browser
// only ever talks to one origin and cookies/tokens behave the same as
// production, where FastAPI serves this app's build output directly.
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            "/api": {
                target: (_a = process.env.MINIP7_API_URL) !== null && _a !== void 0 ? _a : "http://localhost:8000",
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: "dist",
        sourcemap: true,
    },
});
