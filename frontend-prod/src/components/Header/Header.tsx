import React, { MouseEvent, useState } from 'react';
import { AppBar, Toolbar, IconButton, Menu, MenuItem, Box } from '@mui/material';
import {useLocation, useNavigate} from 'react-router-dom';
import { useDispatch } from 'react-redux';
import {ArrowDownSVG} from "../../assets/ArrowDownSVG";
import {Typography} from "../Typography";
import {logout} from "../../features/auth/authSlice";

export const Header: React.FC = () => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const location = useLocation();

    const handleMenu = (event: MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleLogOut = () => {
        handleClose();
        localStorage.removeItem('token');
        localStorage.removeItem('refresh');
        dispatch(logout());
    };

    if (location.pathname !== '/search-client' && location.pathname !== '/' && location.pathname !== '/client-contacted') {
        return null;
    }

    return (
        <AppBar position="static" style={{ backgroundColor: 'white', boxShadow: 'none' }}>
            <Toolbar>
                <Box flexGrow={1} />
                <IconButton
                    edge="end"
                    color="inherit"
                    aria-label="menu"
                    aria-controls="menu-appbar"
                    aria-haspopup="true"
                    onClick={handleMenu}
                >
                    <img
                        src={require("../../assets/headerIcon.png")}
                        alt="logo"
                        style={{
                            width: "32px",
                            marginRight: "5px"
                        }}
                    />
                    <ArrowDownSVG isRotate={!!anchorEl}/>
                </IconButton>
                <Menu
                    id="menu-appbar"
                    anchorEl={anchorEl}
                    anchorOrigin={{
                        vertical: 'bottom',
                        horizontal: 'right',
                    }}
                    keepMounted
                    transformOrigin={{
                        vertical: 'top',
                        horizontal: 'right',
                    }}
                    open={open}
                    onClose={handleClose}
                >
                    {location.pathname === '/client-contacted' ? <MenuItem onClick={() =>
                        {
                            navigate("/search-client")
                            handleClose()
                        }} style={{padding: "0px 20px"}}><Typography variant="body1">Search Clients</Typography></MenuItem> : null}
                    {location.pathname === '/search-client' || location.pathname === '/' ? <MenuItem onClick={() =>
                        {
                            navigate("/client-contacted")
                            handleClose()
                        } } style={{padding: "0px 20px"}}><Typography variant="body1">Clients Contacted</Typography></MenuItem> : null}
                    <MenuItem onClick={handleLogOut} style={{padding: "0px 20px"}}><Typography variant="body1">Logout</Typography></MenuItem>
                </Menu>
            </Toolbar>
        </AppBar>
    );
};
