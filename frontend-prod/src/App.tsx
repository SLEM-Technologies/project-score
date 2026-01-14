import './App.css';
import React, {FC} from "react";
import { ThemeProvider } from '@mui/material/styles';
import {SnackbarProvider} from "notistack";
import {theme} from "./theme";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import {PrivateRoute} from "./components";
import LoginScreen from "./screens/LoginScreen";
import SearchClientScreen from "./screens/SeacrhClient";
import NotFound from "./screens/NotFoundScreen";
import ClientTableScreen from "./screens/ClientTableScreen";
import {Header} from "./components/Header";

export const App: FC = () => (
    <ThemeProvider theme={theme}>
        <SnackbarProvider anchorOrigin={{
            vertical: 'top',
            horizontal: 'center',
        }}>
            <BrowserRouter>
                <Header />
                <Routes>
                    <Route path="/" element={<PrivateRoute/>}>
                        <Route path='/' element={<SearchClientScreen/>}/>
                    </Route>
                    <Route path="/login" element={<LoginScreen/>} />
                    <Route path="/search-client" element={<PrivateRoute/>}>
                        <Route path='/search-client' element={<SearchClientScreen/>}/>
                    </Route>
                    <Route path="*" element={<NotFound/>} />
                    <Route path="/client-contacted" element={<PrivateRoute/>}>
                        <Route path='/client-contacted' element={<ClientTableScreen/>}/>
                    </Route>
                </Routes>
            </BrowserRouter>
        </SnackbarProvider>
    </ThemeProvider>
)

export default App;
