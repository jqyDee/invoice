import React, {useState} from 'react'
import {Button} from 'primereact/button'
import {InputText} from 'primereact/inputtext'
import {Password} from 'primereact/password'
import {useAuth} from '../contexts/auth-context.tsx'
import {useGlobalToast} from '../hooks/use-global-toast.ts'

export const LoginPageView: React.FC = () => {
    const {login} = useAuth()
    const {showToast} = useGlobalToast()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.SubmitEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            await login(username, password)
        } catch {
            showToast({severity: 'error', summary: 'Fehler', detail: 'Ungültige Anmeldedaten', life: 3000})
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex align-items-center justify-content-center" style={{minHeight: '100vh'}}>
            <div className="surface-card p-4 shadow-2 border-round-sm" style={{width: '360px'}}>
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
                    <Button type="submit" label="Anmelden" loading={loading} className="w-full"/>
                </form>
            </div>
        </div>
    )
}
