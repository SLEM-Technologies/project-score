import React, { FC, ChangeEvent } from 'react';
import TextFieldMUI, { TextFieldProps } from '@mui/material/TextField';
import { styled } from '@mui/system';
import {colors} from "../../constants";
import { InputMask, type InputMaskProps } from '@react-input/mask';
import { forwardRef } from 'react';

interface CustomTextFieldProps extends Omit<TextFieldProps, 'variant'> {
    variant?: 'standard' | 'outlined' | 'filled';
    onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
}

const StyledTextField = styled(TextFieldMUI as React.ComponentType<any>)<{ variant?: string }>(({ variant }) => ({
    margin: 0,
    '& .MuiInput-root': {
        backgroundColor: variant === 'filled' ? 'lightgray' : 'inherit',
    },
    '& .MuiFormLabel-root': {
        color: colors.PRIMARY_COLOR,
        '&:focused': {
            borderColor: colors.PRIMARY_COLOR,
        },
    },
    '& .MuiInputBase-root': {
        minHeight: "48px",
        borderRadius: "6px",
        borderWidth: "5px",
        borderColor: colors.PRIMARY_COLOR,
    },
    '& .MuiOutlinedInput-root': {
        '& fieldset': {
            borderColor: colors.PRIMARY_COLOR,
        },
        '&:hover fieldset': {
            borderColor: colors.PRIMARY_COLOR,
        },
        '&.Mui-focused fieldset': {
            borderColor: colors.PRIMARY_COLOR,
        },
    },
}));

const ForwardedInputMask = forwardRef<HTMLInputElement, InputMaskProps>((props, forwardedRef) => {
    return <InputMask ref={forwardedRef} mask="(___) ___-____" replacement={{ _: /\d/ }} {...props} />;
});
ForwardedInputMask.displayName = 'ForwardedInputMask';

export const TextField: FC<CustomTextFieldProps> = ({ variant = 'standard', onChange, type,...rest }) => {
    return (
       type === "tel" ? <StyledTextField variant={variant} onChange={onChange} InputProps={{
                inputComponent: ForwardedInputMask,
            }} {...rest}  /> : <StyledTextField variant={variant} type={type} onChange={onChange} {...rest}  />
    );
};
