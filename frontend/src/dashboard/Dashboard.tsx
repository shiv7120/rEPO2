import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../auth/AuthContext'

export default function Dashboard() {
	const { user, logout } = useAuth()
	const [accounts, setAccounts] = useState<any[]>([])
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState('')

	const refresh = async () => {
		setLoading(true)
		setError('')
		try {
			const res = await api.get('/accounts')
			setAccounts(res.data)
		} catch (err: any) {
			setError(err?.response?.data?.message || 'Failed to load accounts')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => { refresh() }, [])

	const createAccount = async () => {
		await api.post('/accounts', { account_type: 'checking' })
		refresh()
	}

	return (
		<div className="dashboard">
			<div className="row between">
				<h2>Welcome {user?.full_name}</h2>
				<button onClick={logout}>Logout</button>
			</div>
			{loading ? <p>Loading...</p> : error ? <p className="error">{error}</p> : (
				<>
					<button onClick={createAccount}>Create Account</button>
					<div className="list">
						{accounts.map(acc => (
							<div key={acc.id} className="card">
								<div className="row between">
									<strong>{acc.account_type.toUpperCase()}</strong>
									<span>#{acc.account_number}</span>
								</div>
								<div className="row between">
									<span>Balance</span>
									<strong>${acc.balance.toFixed(2)}</strong>
								</div>
							</div>
						))}
					</div>
				</>
			)}
		</div>
	)
}