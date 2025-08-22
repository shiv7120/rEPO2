import { FormEvent, useState } from 'react'
import { useAuth } from './AuthContext'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
	const { login } = useAuth()
	const navigate = useNavigate()
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState('')
	const [loading, setLoading] = useState(false)

	const onSubmit = async (e: FormEvent) => {
		e.preventDefault()
		setError('')
		setLoading(true)
		try {
			await login(email, password)
			navigate('/')
		} catch (err: any) {
			setError(err?.response?.data?.message || 'Login failed')
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="card">
			<h1>Login</h1>
			<form onSubmit={onSubmit}>
				<label>Email</label>
				<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
				<label>Password</label>
				<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
				<button disabled={loading} type="submit">{loading ? 'Loading...' : 'Login'}</button>
				{error && <p className="error">{error}</p>}
			</form>
		</div>
	)
}