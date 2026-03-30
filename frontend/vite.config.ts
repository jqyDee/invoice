import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'
import pkg from './package.json'

export default defineConfig({
    plugins: [
        react(),
    ],
    server: {
        proxy: {
            '/api': {
                target: process.env.BACKEND_URL ?? 'http://localhost:8000',
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
    },
    define: {
        'import.meta.env.PACKAGE_VERSION': JSON.stringify(pkg.version),
    },
})