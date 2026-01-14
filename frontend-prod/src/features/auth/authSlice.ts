import { createSlice } from '@reduxjs/toolkit'

interface AuthState {
    loggedIn: boolean
}

const initialState: AuthState = { loggedIn: Boolean(localStorage.getItem('token')) }

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        authorize(state) {
            state.loggedIn = true
        },
        logout(state) {
            state.loggedIn = false
        },
    },
})

export const { authorize, logout } = authSlice.actions

export default authSlice.reducer
