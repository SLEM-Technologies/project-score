import React from 'react';
import {Typography} from "../components";
import {Container} from "@mui/material";

const NotFound: React.FC = () => {
    return (
        <Container maxWidth="md" style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
        }}>
            <Typography variant="h2">404 - Page Not Found</Typography>
            <Typography variant="h5">The requested page does not exist.</Typography>
        </Container>
    );
};

export default NotFound;
