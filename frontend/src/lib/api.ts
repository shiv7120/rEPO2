import axios from 'axios'

const instance = axios.create({
	baseURL: '/api'
})

function setToken(token: string | null) {
	if (token) {
		instance.defaults.headers.common['Authorization'] = `Bearer ${token}`
	} else {
		delete instance.defaults.headers.common['Authorization']
	}
}

export const api = Object.assign(instance, { setToken })