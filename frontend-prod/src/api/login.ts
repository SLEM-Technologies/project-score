import axios, {AxiosResponse} from 'axios';

interface LoginData {
    email: string;
    password: string;
}

export interface LoginResponse {
    access: string;
    refresh: string;
}

const apiEndpoint = process.env.REACT_APP_API_URL;


export const login = async (data: LoginData) => {
    try {
        const response: AxiosResponse<LoginResponse> = await axios.post( apiEndpoint + 'api/v1/auth/token/', data);
        console.log(response);
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refresh', response.data.refresh);
        localStorage.setItem('tokenExpiry', (new Date().getTime() +  12 * 60 * 60 * 1000).toString()); // +12 hours
        localStorage.setItem('refreshExpiry', (new Date().getTime() + 24 * 60 * 60 * 1000).toString()); // +25 hours
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

export const checkTokenExpiry = async () => {
    const tokenExpiry = Number(localStorage.getItem('tokenExpiry'));
    const refreshExpiry = Number(localStorage.getItem('refreshExpiry'));
    const currentTime = new Date().getTime();

    if (!tokenExpiry || !refreshExpiry || currentTime > refreshExpiry) {
        localStorage.clear();
        return true;
    } else if (currentTime > tokenExpiry) {
        const refreshToken = localStorage.getItem('refresh');
        const response: AxiosResponse<LoginResponse> = await axios.post(apiEndpoint + 'api/v1/auth/token/refresh/', {refresh: refreshToken});
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refresh', response.data.refresh);
        localStorage.setItem('tokenExpiry', (new Date().getTime() + 12 * 60 * 60 * 1000).toString()); // +12 hours
        localStorage.setItem('refreshExpiry', (new Date().getTime() + 24 * 60 * 60 * 1000).toString()); //
        return false;
    }
};

