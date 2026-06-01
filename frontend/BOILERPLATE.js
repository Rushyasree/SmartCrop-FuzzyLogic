/**
 * CROP ZEN FRONTEND - REACT DASHBOARD
 * 
 * This is a starter template showing the core structure and key components.
 * Files should be organized as shown in SETUP_GUIDE.md
 * 
 * To build the complete frontend:
 * 1. Run: npm install
 * 2. Create directories as per package.json scripts
 * 3. Copy these templates to appropriate files
 * 4. Run: npm run dev
 */

// ============================================================================
// FILE: src/main.jsx - React Entry Point
// ============================================================================
/*
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import App from './App'
import { store } from './redux/store'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
)
*/

// ============================================================================
// FILE: src/index.css - Global Styles
// ============================================================================
/*
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  @apply antialiased;
}

body {
  @apply bg-light text-dark;
  font-family: 'Inter', system-ui, sans-serif;
}

/* Custom animations */
@layer utilities {
  .fade-in {
    @apply animate-fadeIn;
  }
  
  .slide-in {
    @apply animate-slideIn;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
*/

// ============================================================================
// FILE: src/App.jsx - Main App Component
// ============================================================================
/*
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { setUser } from './redux/slices/authSlice'

// Pages
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import FarmPage from './pages/FarmPage'
import PredictionPage from './pages/PredictionPage'
import SettingsPage from './pages/SettingsPage'

// Components
import ProtectedRoute from './components/Common/ProtectedRoute'

export default function App() {
  const dispatch = useDispatch()

  useEffect(() => {
    // Load user from localStorage on app start
    const user = localStorage.getItem('user')
    if (user) {
      try {
        dispatch(setUser(JSON.parse(user)))
      } catch (error) {
        console.error('Failed to load user:', error)
      }
    }
  }, [dispatch])

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/farms"
          element={
            <ProtectedRoute>
              <FarmPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/predictions"
          element={
            <ProtectedRoute>
              <PredictionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
*/

// ============================================================================
// FILE: src/services/apiClient.js - Axios with JWT
// ============================================================================
/*
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_URL}/auth/refresh-token`, {
          refresh_token: refreshToken
        })

        const { access_token } = response.data.data
        localStorage.setItem('access_token', access_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch (err) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(err)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
*/

// ============================================================================
// FILE: src/services/authService.js - Auth API
// ============================================================================
/*
import apiClient from './apiClient'

export const authService = {
  register: async (data) => {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password })
    const { access_token, refresh_token, user } = response.data.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user', JSON.stringify(user))
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  }
}
*/

// ============================================================================
// FILE: src/services/farmService.js - Farm API
// ============================================================================
/*
import apiClient from './apiClient'

export const farmService = {
  getFarms: async (page = 1, perPage = 10) => {
    const response = await apiClient.get('/farms', {
      params: { page, per_page: perPage }
    })
    return response.data
  },

  getFarmById: async (id) => {
    const response = await apiClient.get(`/farms/${id}`)
    return response.data
  },

  createFarm: async (data) => {
    const response = await apiClient.post('/farms', data)
    return response.data
  },

  updateFarm: async (id, data) => {
    const response = await apiClient.put(`/farms/${id}`, data)
    return response.data
  },

  deleteFarm: async (id) => {
    const response = await apiClient.delete(`/farms/${id}`)
    return response.data
  }
}
*/

// ============================================================================
// FILE: src/services/predictionService.js - Prediction API
// ============================================================================
/*
import apiClient from './apiClient'

export const predictionService = {
  getPredictions: async (page = 1, perPage = 10) => {
    const response = await apiClient.get('/predictions', {
      params: { page, per_page: perPage }
    })
    return response.data
  },

  createPrediction: async (data) => {
    const response = await apiClient.post('/predictions', data)
    return response.data
  },

  makePrediction: async (soilPH, moisture, image = null) => {
    const formData = new FormData()
    formData.append('soilPH', soilPH)
    formData.append('moisture', moisture)
    if (image) {
      formData.append('image', image)
    }

    const response = await apiClient.post('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}
*/

// ============================================================================
// FILE: src/redux/store.js - Redux Store
// ============================================================================
/*
import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import farmsReducer from './slices/farmsSlice'
import predictionsReducer from './slices/predictionsSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    farms: farmsReducer,
    predictions: predictionsReducer
  }
})
*/

// ============================================================================
// FILE: src/redux/slices/authSlice.js - Auth State
// ============================================================================
/*
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { authService } from '../../services/authService'

export const login = createAsyncThunk('auth/login', async ({ email, password }) => {
  const response = await authService.login(email, password)
  return response.data.user
})

export const register = createAsyncThunk('auth/register', async (userData) => {
  const response = await authService.register(userData)
  return response.data.user
})

export const getCurrentUser = createAsyncThunk('auth/getCurrentUser', async () => {
  const response = await authService.getCurrentUser()
  return response.data
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false
  },
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload
      state.isAuthenticated = !!action.payload
    },
    logout: (state) => {
      authService.logout()
      state.user = null
      state.isAuthenticated = false
    },
    clearError: (state) => {
      state.error = null
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload
        state.isAuthenticated = true
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload
        state.isAuthenticated = true
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
  }
})

export const { setUser, logout, clearError } = authSlice.actions
export default authSlice.reducer
*/

// ============================================================================
// FILE: src/redux/slices/farmsSlice.js - Farms State
// ============================================================================
/*
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { farmService } from '../../services/farmService'

export const fetchFarms = createAsyncThunk('farms/fetchFarms', async ({ page = 1 } = {}) => {
  const response = await farmService.getFarms(page)
  return response.data
})

export const createFarm = createAsyncThunk('farms/createFarm', async (farmData) => {
  const response = await farmService.createFarm(farmData)
  return response.data
})

export const updateFarm = createAsyncThunk('farms/updateFarm', async ({ id, data }) => {
  const response = await farmService.updateFarm(id, data)
  return response.data
})

export const deleteFarm = createAsyncThunk('farms/deleteFarm', async (id) => {
  await farmService.deleteFarm(id)
  return id
})

const farmsSlice = createSlice({
  name: 'farms',
  initialState: {
    farms: [],
    loading: false,
    error: null,
    pagination: { page: 1, total: 0, pages: 0 }
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFarms.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchFarms.fulfilled, (state, action) => {
        state.loading = false
        state.farms = action.payload
        state.pagination = action.meta.arg
      })
      .addCase(fetchFarms.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
      .addCase(createFarm.fulfilled, (state, action) => {
        state.farms.push(action.payload)
      })
      .addCase(deleteFarm.fulfilled, (state, action) => {
        state.farms = state.farms.filter((farm) => farm.id !== action.payload)
      })
  }
})

export const { clearError } = farmsSlice.actions
export default farmsSlice.reducer
*/

// ============================================================================
// FILE: src/components/Common/ProtectedRoute.jsx - Route Guard
// ============================================================================
/*
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useSelector((state) => state.auth)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}
*/

// ============================================================================
// FILE: src/hooks/useAuth.js - Custom Auth Hook
// ============================================================================
/*
import { useDispatch, useSelector } from 'react-redux'
import { useCallback } from 'react'
import { login, logout, register } from '../redux/slices/authSlice'

export function useAuth() {
  const dispatch = useDispatch()
  const { user, isAuthenticated, loading, error } = useSelector((state) => state.auth)

  const handleLogin = useCallback((email, password) => {
    return dispatch(login({ email, password }))
  }, [dispatch])

  const handleRegister = useCallback((userData) => {
    return dispatch(register(userData))
  }, [dispatch])

  const handleLogout = useCallback(() => {
    dispatch(logout())
  }, [dispatch])

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout
  }
}
*/

// ============================================================================
// FILE: src/utils/validators.js - Form Validators
// ============================================================================
/*
export const validators = {
  email: (email) => {
    const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/
    return regex.test(email)
  },

  password: (password) => {
    return password.length >= 8
  },

  phone: (phone) => {
    return phone.length >= 10
  },

  farmName: (name) => {
    return name && name.length > 0 && name.length <= 100
  },

  farmSize: (size) => {
    return size > 0 && size <= 10000
  },

  soilPH: (ph) => {
    return ph >= 3.0 && ph <= 10.0
  },

  moisture: (moisture) => {
    return moisture >= 0 && moisture <= 100
  }
}
*/

// ============================================================================
// FILE: src/utils/formatters.js - Data Formatters
// ============================================================================
/*
export const formatters = {
  date: (date) => {
    return new Date(date).toLocaleDateString()
  },

  dateTime: (dateTime) => {
    return new Date(dateTime).toLocaleString()
  },

  currency: (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount)
  },

  percentage: (value) => {
    return `${(value * 100).toFixed(2)}%`
  },

  decimal: (value, places = 2) => {
    return parseFloat(value).toFixed(places)
  }
}
*/

export default {
  note: 'This file contains boilerplate code for the React frontend. Copy each section to its respective file.'
}
