import axios, {AxiosError} from 'axios';

export const getUser = async () => {
    const token = localStorage.getItem('token');
    const headers = {
        Authorization: `Bearer ${token}`,
    };
    try {
        const response = await axios.get("https://64aaeacd0c6d844abedefaf6.mockapi.io/api/v1/auth/5", {headers});
        return response.data;
    } catch (err) {
        const error = err as AxiosError;
        if (error.response && error.response.status === 401) {
            const refreshToken = localStorage.getItem('refreshToken');
            const refreshResponse = await axios.post('/api/auth/refresh', { token: refreshToken });
            if (refreshResponse.data.token) {
                localStorage.setItem('token', refreshResponse.data.token);
                headers.Authorization = `Bearer ${refreshResponse.data.token}`;
                const retryResponse = await axios.get("/refresh", {headers});
                return retryResponse.data;
            }
            else {
                localStorage.removeItem('token');
                throw error;
            }
        } else {
            localStorage.removeItem('token');
            localStorage.removeItem('refresh');
            throw error
        }
    }
};
