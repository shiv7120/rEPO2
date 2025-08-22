import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'

type User = {
	id: number
	email: string
	full_name: string
}

type AuthContextValue = {
	token: string | null
	user: User | null
	login: (email: string, password: string) => Promise<void>
	logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
	const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
	const [user, setUser] = useState<User | null>(null)

	useEffect(() => {
		if (token) {
			api.setToken(token)
			api.get('/auth/me').then((res) => setUser(res.data)).catch(() => setUser(null))
		}
	}, [token])

	const login = async (email: string, password: string) => {
		const res = await api.post('/auth/login', { email, password })
		setToken(res.data.access_token)
		localStorage.setItem('token', res.data.access_token)
		setUser(res.data.user)
	}

	const logout = () => {
		setToken(null)
		setUser(null)
		localStorage.removeItem('token')
		api.setToken(null)
	}

	const value = useMemo(() => ({ token, user, login, logout }), [token, user])
	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
	const ctx = useContext(AuthContext)
	if (!ctx) throw new Error('useAuth must be used within AuthProvider')
	return ctx
}