import React, {createContext, useCallback, useContext, useEffect, useMemo, useRef, useState} from 'react'
import {useNavigate} from 'react-router-dom'
import {useMutation} from '@tanstack/react-query'
import {loginAuthTokenPostMutation, refreshTokenAuthRefreshPostMutation} from '../api/@tanstack/react-query.gen'
import {ROUTES} from '../config/routes.ts'

const SESSION_DURATION_MS = 3 * 60 * 60 * 1000  // 3 Hours

interface AuthContextValue {
    token: string | null
    isAuthenticated: boolean
    login: (username: string, password: string) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({children}) => {
    const navigate = useNavigate()
    const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const [token, setToken] = useState<string | null>(() => {
        const stored = localStorage.getItem('token')
        if (!stored) return null
        try {
            const payload = JSON.parse(atob(stored.split('.')[1]))
            if (payload.exp * 1000 < Date.now()) {
                localStorage.removeItem('token')
                return null
            }
        } catch {
            localStorage.removeItem('token')
            return null
        }
        return stored
    })

    const {mutateAsync: loginAsync} = useMutation(loginAuthTokenPostMutation())
    const {mutateAsync: refreshAsync} = useMutation(refreshTokenAuthRefreshPostMutation())

    const logout = useCallback(() => {
        if (refreshTimerRef.current) {
            clearTimeout(refreshTimerRef.current)
            refreshTimerRef.current = null
        }
        localStorage.removeItem('token')
        localStorage.removeItem('session_start')
        setToken(null)
        navigate(ROUTES.LOGIN)
    }, [navigate])

    const scheduleRefresh = useCallback((currentToken: string) => {
        if (refreshTimerRef.current) {
            clearTimeout(refreshTimerRef.current)
        }
        try {
            const payload = JSON.parse(atob(currentToken.split('.')[1]))
            const remaining = payload.exp * 1000 - Date.now()
            if (remaining <= 0) return
            const delay = remaining * 0.75
            refreshTimerRef.current = setTimeout(async () => {
                const sessionStart = Number(localStorage.getItem('session_start') ?? 0)
                if (Date.now() - sessionStart > SESSION_DURATION_MS) {
                    logout()
                    return
                }
                try {
                    const data = await refreshAsync({auth: currentToken}) as { access_token: string }
                    const newToken = data.access_token
                    localStorage.setItem('token', newToken)
                    setToken(newToken)
                    scheduleRefresh(newToken)
                } catch {
                    // silent failure — 401 interceptor handles forced logout
                }
            }, delay)
        } catch {
            // invalid token shape — ignore
        }
    }, [refreshAsync, logout])

    useEffect(() => {
        if (token) {
            scheduleRefresh(token)
        }
        return () => {
            if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current)
        }
    }, [])

    useEffect(() => {
        const handleVisibility = () => {
            if (document.visibilityState === 'visible') {
                const stored = localStorage.getItem('token')
                if (stored) {
                    try {
                        const payload = JSON.parse(atob(stored.split('.')[1]))
                        if (payload.exp * 1000 < Date.now()) {
                            logout()
                            return
                        }
                    } catch { /* ignore */
                    }
                    scheduleRefresh(stored)
                }
            } else {
                if (refreshTimerRef.current) {
                    clearTimeout(refreshTimerRef.current)
                    refreshTimerRef.current = null
                }
            }
        }
        document.addEventListener('visibilitychange', handleVisibility)
        return () => document.removeEventListener('visibilitychange', handleVisibility)
    }, [scheduleRefresh, logout])

    const login = useCallback(async (username: string, password: string) => {
        const data = await loginAsync({body: {username, password}}) as { access_token: string }
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('session_start', String(Date.now()))
        setToken(data.access_token)
        scheduleRefresh(data.access_token)
        navigate(ROUTES.HOME)
    }, [navigate, loginAsync, scheduleRefresh])

    const value = useMemo<AuthContextValue>(() => ({
        token,
        isAuthenticated: token !== null,
        login,
        logout,
    }), [token, login, logout])

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = (): AuthContextValue => {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used within AuthProvider')
    return ctx
}
