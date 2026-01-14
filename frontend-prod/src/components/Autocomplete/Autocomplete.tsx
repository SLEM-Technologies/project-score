import React, { FC, forwardRef } from 'react';
import AutocompleteMUI, {AutocompleteProps} from '@mui/material/Autocomplete';
import {TextField} from "../TextField";


interface CustomAutocompleteProps extends Omit<AutocompleteProps<any, any, any, any>, 'variant' | 'renderInput'> {
    variant: 'standard' | 'outlined' | 'filled';
    label?: string;
    autocompleteRef?: any;
}

const AutocompleteComponent: FC<CustomAutocompleteProps> = forwardRef(({ variant = 'outlined', options, label, ...rest }, autocompleteRef) => {
    return (
        <AutocompleteMUI
            options={options}
            noOptionsText="No results found"
            renderInput={(params) => <TextField {...params} variant={variant} label={label}
                                                inputRef={autocompleteRef}/>}
            {...rest}
        />
    )
})
AutocompleteComponent.displayName = 'AutocompleteComponent';

export const Autocomplete = AutocompleteComponent;
