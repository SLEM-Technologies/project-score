import React, { FC, ChangeEvent } from 'react';
import CheckboxMUI, { CheckboxProps } from '@mui/material/Checkbox';
import { styled } from '@mui/system';
import { colors } from "../../constants";
import {CheckedIcon} from "../../assets/CheckedIcon";

interface CustomCheckboxProps extends Omit<CheckboxProps, 'variant'> {
    variant?: 'standard' | 'outlined' | 'filled';
    onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
}

const StyledCheckbox = styled(CheckboxMUI as React.ComponentType<any>)<{ variant?: string }>(({ variant }) => ({
    '& .MuiCheckbox-root': {
        color: colors.PRIMARY_COLOR,
        '&:hover': {
            backgroundColor: variant === 'filled' ? 'lightgray' : 'inherit',
        },
    },
    '& .MuiCheckbox-colorSecondary.Mui-checked': {
        color: colors.PRIMARY_COLOR,
    },
    '& .MuiCheckbox-colorSecondary.Mui-unchecked': {
        color: colors.PRIMARY_COLOR,
    },
}));

export const Checkbox: FC<CustomCheckboxProps> = ({ variant = 'standard', onChange, ...rest }) => {
    return (
        <StyledCheckbox variant={variant} onChange={onChange} checkedIcon={<CheckedIcon/>} {...rest} />
    );
};
