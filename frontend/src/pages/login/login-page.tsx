import React, { useState } from 'react'
import { Button } from 'primereact/button'
import { InputText } from 'primereact/inputtext'
import { Password } from 'primereact/password'
import { useAuth } from '../../contexts/auth-context.tsx'

export const LoginPage: React.FC = () => {
    const { login } = useAuth()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.SubmitEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)
        try {
            await login(username, password)
        } catch {
            setError('Ungültige Anmeldedaten')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
            <div className="surface-card p-4 shadow-2 border-round" style={{ width: '360px' }}>
                <h2 className="text-center mt-0 mb-4">Anmelden</h2>
                <form onSubmit={handleSubmit} className="flex flex-column gap-3 p-fluid">
                    <div className="flex flex-column gap-1">
                        <label htmlFor="username">Benutzername</label>
                        <InputText
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            autoComplete="username"
                            required
                        />
                    </div>
                    <div className="flex flex-column gap-1">
                        <label htmlFor="password">Passwort</label>
                        <Password
                            inputId="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            feedback={false}
                            toggleMask
                            autoComplete="current-password"
                            required
                        />
                    </div>
                    {error && <small className="p-error">{error}</small>}
                    <Button type="submit" label="Anmelden" loading={loading} className="w-full" />
                </form>
            </div>
        </div>
    )
}
