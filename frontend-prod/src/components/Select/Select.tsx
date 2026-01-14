import React, { FC } from 'react';
import {SelectProps} from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import {TextField} from "../TextField";

interface OptionType {
    value: string | number | boolean;
    label: string;
}

interface CustomSelectProps extends Omit<SelectProps, 'variant'> {
    variant: 'standard' | 'outlined' | 'filled';
    label?: string;
    options: OptionType[];
}

const SelectComponent: FC<CustomSelectProps> = ({ variant = 'outlined', options, label, ...rest }) => {
    return (
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        <TextField
            select
            variant={variant}
            label={label}
            SelectProps={{
                MenuProps: {
                    anchorOrigin: {
                        vertical: 'bottom',
                        horizontal: 'left',
                    },
                    transformOrigin: {
                        vertical: 'top',
                        horizontal: 'left',
                    },
                    MenuListProps: {
                        style: {
                            maxWidth: '500px',
                            maxHeight: "400px"
                        }
                    }
                }
            }}
            {...rest}
        >
            {options.map((option, index) => (
                <MenuItem style={{whiteSpace: "unset", wordBreak: "break-all"}} key={index} value={option.value as string}>
                    {option.label}
                </MenuItem>
            ))}
        </TextField>
    )
}
SelectComponent.displayName = 'SelectComponent';

export const Select = SelectComponent;
