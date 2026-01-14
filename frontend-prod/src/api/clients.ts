import axios, {AxiosResponse} from 'axios';
import {checkTokenExpiry} from "./login";

export interface IContactedInfo {
    count: number,
    next: string,
    prev: string,
    results: IContacted[]
}

export interface IContacted {
    client_id: string,
    emails: IEmail[],
    phones: IPhone[],
    patients: {name: string, odu_id: string}[],
    full_name: string,
    is_followed: boolean,
    practice_id: string,
    practice_name: string,
    sent_at: string,
    sms_history_id: string,
}

interface SearchData {
    search: string;
    phone_number: string;
}

export interface IClientsList {
    "odu_id": string,
    "first_name": string,
    "last_name": string,
    "full_name": string,
    "email_address": string | null,
    "phone_number": string | null
}

export interface IPhone {
    app_number: string,
    odu_id: string,
}

export interface IEmail {
    address: string,
    odu_id: string,
}

interface IClient {
    odu_id: string,
    first_name: string,
    last_name: string,
    full_name?: string,
    emails: IEmail[],
    phones: IPhone[],
    practices: [{
        name: string,
        odu_id: string,
    }]
    patients?: IPatient[]
}

interface IPatient {
    "odu_id": string,
    "species_description": string,
    "breed_description": string,
    "gender_description": string,
    "name": string,
    "patient_age": number,
    "outcome": null | string,
    "opt_out": null | string,
    "comment": null | string,
    "reminders": IReminders[],
    "last_appointment": {
        date?: string
    },
    "next_appointments": {date: string}[],
    "outcome_at": Date
}


interface IReminders {
    "date_due": string,
    "description": string,
    "sms_status": string
}

export interface IPractices {
    mapping: {
        [key: string]: string[]
    },
    practices: {
        name: string,
        odu_id: string,
        scheduler: string,
    }[],
}

const apiEndpoint = process.env.REACT_APP_API_URL;


export const getClients = async (data: SearchData) => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<IClientsList[]> = await axios.get( apiEndpoint + 'api/v1/call-center/clients/', {
            params: data, headers
        });
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

export const getClientInfo = async (id: string) => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<IClient> = await axios.get( apiEndpoint + `api/v1/call-center/clients/${id}`, {
            headers
        });
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
};

export const getOutcomes = async () => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<string[]> = await axios.get( apiEndpoint + `/api/v1/call-center/outcomes`, {
            headers
        });
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
}

export const updateClient = async (id: string, data: any) => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<string[]> = await axios.patch( apiEndpoint + `api/v1/call-center/clients/${id}`, data
        , {headers});
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
}

export const getFAQ = async (id: string) => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<{question: string, answer: string}[]> = await axios.get( apiEndpoint + `api/v1/call-center/faq/${id}`,
            {headers});
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
}

export const getContactedInfo = async (
    {limit, offset, name, followed, sent_after, sent_before, practice}
        : { limit: number, offset: number, name?: string, followed?: boolean, sent_after?: string, sent_before?: string, practice?: string[] }) => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<IContactedInfo> = await axios.get( apiEndpoint + `api/v1/call-center/clients/contacted/`,
            {params: {limit, offset, name, followed, sent_after, sent_before, practice: practice ? practice.join(',') : undefined}, headers});
        return response.data;
    }
    catch (error) {
        console.error(error);
        throw error;
    }
}

export const switchSMS = async (sms_id: string) => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<{is_followed: boolean, uuid: string}> = await axios.patch( apiEndpoint + `api/v1/call-center/sms/${sms_id}/switch/`, {},
            {headers});
        return response.data;
        }
    catch (error) {
        console.error(error);
        throw error;
    }
}

export const getPractices = async () => {
    try {
        await checkTokenExpiry();
        const token = localStorage.getItem('token');
        const headers = {
            Authorization: `Bearer ${token}`,
        };
        const response: AxiosResponse<IPractices> = await axios.get( apiEndpoint + `api/v1/call-center/practices/`,
            {headers});
        return response.data;
        }
    catch (error) {
        console.error(error);
        throw error;
    }
};
