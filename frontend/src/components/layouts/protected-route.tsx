import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/auth-context.tsx'
import { ROUTES } from '../../config/routes.ts'

export const ProtectedRoute: React.FC = () => {
    const { isAuthenticated } = useAuth()
    return isAuthenticated ? <Outlet /> : <Navigate to={ROUTES.LOGIN} replace />
}
