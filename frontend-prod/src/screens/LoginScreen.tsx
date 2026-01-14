import React, {useEffect, useState} from 'react';
import {useDispatch, useSelector} from 'react-redux';
import {Button, TextField} from "../components";
import { Grid, Container, CircularProgress, Backdrop} from '@mui/material';
import { authorize } from '../features/auth/authSlice'
import {login} from "../api";
import { useSnackbar } from 'notistack';
import {useNavigate} from "react-router-dom";
import {LoginResponse} from "../api/login";
import {RootState} from "../app/store";

const LoginScreen = () => {
    const navigate = useNavigate();
    const { loggedIn } = useSelector((state: RootState) => state.auth);
    const { enqueueSnackbar } = useSnackbar();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [credentials, setCredentials] = useState({
        email: '',
        password: '',
    });

    useEffect(() => {
        if (loggedIn) {
            navigate('/search-client');
        }
    });

    const dispatch = useDispatch();

    const handleSubmit = async () => {
        try {
            setIsLoading(true);
            if (!credentials.email || !credentials.password) {
                enqueueSnackbar(`Please fill in the ${credentials.email ? 'password' : 'email'}`, { variant: 'error' });
                return;
            }
            const data: LoginResponse = await login(credentials);
            if (data.access) {
                dispatch(authorize());
                navigate("/search-client");
            } else {
                enqueueSnackbar('Error', {
                    variant: 'error',
                });
            }
        } catch (error) {
            enqueueSnackbar('Invalid Email or Password', { variant: 'error' });
        }
        finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="md" style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
        }}>
            <img
                src={require("../assets/logo.png")}
                alt="logo"
                style={{
                    width: "436px",
                    marginBottom: "26px",
                }}
            />
            <Grid item>
                <TextField variant="outlined" label="Email address" fullWidth type="email" style={{marginBottom: "24px"}}
                           onChange={(e) => setCredentials({ ...credentials, email: e.target.value })} />
                <TextField variant="outlined" label="Password" fullWidth type="password" style={{marginBottom: "24px"}}
                           onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}/>
                <Button variant="contained" fullWidth onClick={handleSubmit}>Sign In</Button>
            </Grid>
            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                open={isLoading}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
        </Container>
    );
};

export default LoginScreen;
