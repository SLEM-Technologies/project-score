import React from 'react';
import TypographyMUI, { TypographyProps } from '@mui/material/Typography';
import { styled } from '@mui/system';
import {colors} from "../../constants";

const StyledTypography = styled(TypographyMUI as React.ComponentType<any>)({
    color: colors.PRIMARY_COLOR,
});

type CustomTypographyProps = TypographyProps

export const Typography: React.FC<CustomTypographyProps> = (props) => {
    return <StyledTypography {...props} />;
};
