import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from "@sentry/react";
import './index.css'
import App from './App.tsx'
import { client } from './api/client.gen'

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

client.setConfig({baseUrl: '/api'})

client.interceptors.request.use((request) => {
    const token = localStorage.getItem('token')
    if (!token) return request
    const headers = new Headers(request.headers)
    headers.set('Authorization', `Bearer ${token}`)
    return new Request(request, {headers})
})

client.interceptors.response.use((response) => {
    if (response.status === 401 && !response.url.includes('/auth/token')) {
        localStorage.removeItem('token')
        window.location.href = '/login'
    }

    if (response.status >= 500) {
        Sentry.captureException(new Error(`API Error ${response.status}: ${response.url}`));
    }

    return response
})

const root = createRoot(document.getElementById('root')!, {
    onUncaughtError: Sentry.reactErrorHandler(),
    onCaughtError: Sentry.reactErrorHandler(),
    onRecoverableError: Sentry.reactErrorHandler(),
});

root.render(
    <StrictMode>
        <Sentry.ErrorBoundary fallback={<div>Something went wrong. The team has been notified.</div>}>
            <App/>
        </Sentry.ErrorBoundary>
    </StrictMode>,
)