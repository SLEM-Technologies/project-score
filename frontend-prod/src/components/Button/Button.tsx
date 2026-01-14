import React, { FC, MouseEvent } from 'react';
import ButtonMUI, { ButtonProps } from '@mui/material/Button';
import { styled } from '@mui/system';
import {colors} from "../../constants";

interface CustomButtonProps extends ButtonProps {
    variant?: 'outlined' | 'contained' | 'text';
    onClick?: (event: MouseEvent<HTMLButtonElement>) => void;
}

const StyledButton = styled(ButtonMUI as React.ComponentType<any>)<{ variant?: string }>(({ variant }) => ({
    color: 'white',
    padding: "12px 60px",
    fontSize: "18px",
    lineHeight: "24px",
    fontWeight: 600,
    textTransform: "none",
    borderRadius: "6px",
    border: "none",
    backgroundColor: variant === 'outlined' ? colors.SECONDARY_COLOR : colors.PRIMARY_COLOR,
    '&:hover': {
        backgroundColor: variant === 'outlined' ? colors.SECONDARY_COLOR : colors.PRIMARY_COLOR,
    },
}));

export const Button: FC<CustomButtonProps> = ({ children, variant = 'outlined', onClick, ...rest }) => {
    return (
        <StyledButton variant={variant} onClick={onClick} {...rest}>
            {children}
        </StyledButton>
    );
};
