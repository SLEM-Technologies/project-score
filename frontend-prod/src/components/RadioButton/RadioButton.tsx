import React, { FC, ChangeEvent } from 'react';
import RadioMUI, { RadioProps } from '@mui/material/Radio';
import FormControlLabel from '@mui/material/FormControlLabel';
import { styled } from '@mui/system';
import { colors } from "../../constants";
import {CheckedSVG} from "./CheckedSVG";
import {UncheckedSVG} from "./UncheckedSVG";
import {Typography} from "../Typography";

interface CustomRadioProps extends Omit<RadioProps, 'variant'> {
    variant?: 'standard' | 'outlined' | 'filled';
    onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
    label?: string;
}

const StyledRadio = styled(RadioMUI as React.ComponentType<any>)<{ variant?: string }>(({ variant }) => ({
    '& .MuiRadio-root': {
        margin: 0,
        color: colors.PRIMARY_COLOR,
        '&:hover': {
            backgroundColor: variant === 'filled' ? 'lightgray' : 'inherit',
        },
    },
    '& .MuiRadio-colorSecondary.Mui-checked': {
        color: colors.PRIMARY_COLOR,
    },
}));

export const RadioButton: FC<CustomRadioProps> = ({ variant = 'standard', onChange, label, ...rest }) => {
    return (
        <FormControlLabel
            control={
                <StyledRadio
                    variant={variant}
                    onChange={onChange}
                    checkedIcon={<CheckedSVG />}
                    icon={<UncheckedSVG />}
                    {...rest}
                />
            }
            label={<Typography>{label}</Typography>}
        />
    );
};
