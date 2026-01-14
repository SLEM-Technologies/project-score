import React from "react";
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../../app/store';
import {Outlet} from "react-router-dom";

export const PrivateRoute = () => {
    const { loggedIn } = useSelector((state: RootState) => state.auth);
    const location = useLocation();

    return loggedIn ? (
        <Outlet />
    ) : (
        <Navigate to="/login" state={{ from: location }} replace />
    );
};
