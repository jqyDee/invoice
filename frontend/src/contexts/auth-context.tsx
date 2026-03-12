import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ROUTES } from '../config/routes.ts'

interface AuthContextValue {
    token: string | null
    isAuthenticated: boolean
    login: (username: string, password: string) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const navigate = useNavigate()
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

    const login = useCallback(async (username: string, password: string) => {
        const body = new URLSearchParams({ username, password })
        const response = await fetch('/api/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: body.toString(),
        })
        if (!response.ok) {
            throw new Error('Invalid credentials')
        }
        const data = await response.json()
        localStorage.setItem('token', data.access_token)
        setToken(data.access_token)
        navigate(ROUTES.HOME)
    }, [navigate])

    const logout = useCallback(() => {
        localStorage.removeItem('token')
        setToken(null)
        navigate(ROUTES.LOGIN)
    }, [navigate])

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
