import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { client } from './api/client.gen'

client.setConfig({ baseUrl: '/api' })

client.interceptors.request.use((request) => {
    const token = localStorage.getItem('token')
    if (!token) return request
    const headers = new Headers(request.headers)
    headers.set('Authorization', `Bearer ${token}`)
    return new Request(request, { headers })
})

client.interceptors.response.use((response) => {
    if (response.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
    }
    return response
})

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <App />
    </StrictMode>,
)