import { Route, Routes, Navigate, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import LoginPage from './auth/LoginPage'
import Dashboard from './dashboard/Dashboard'

function ProtectedRoute({ children }: { children: JSX.Element }) {
	const { token } = useAuth()
	if (!token) {
		return <Navigate to="/login" replace />
	}
	return children
}

export default function App() {
	return (
		<AuthProvider>
			<header className="app-header">
				<Link to="/">Bank</Link>
			</header>
			<main className="container">
				<Routes>
					<Route path="/login" element={<LoginPage />} />
					<Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
				</Routes>
			</main>
		</AuthProvider>
	)
}