import React, { FC } from 'react';
import { Table as TableMUI, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import {colors} from "../../constants";
import {Typography} from "../Typography";

interface CustomTableProps {
    columns: Column[];
    data: any[] | undefined
}

interface Column {
    name: string;
    dataIndex: string;
    render?: (record: any) => JSX.Element;
    maxWidth?: string;
}

export const Table: FC<CustomTableProps> = ({ columns, data }) => {
    return (
        <TableContainer style={{boxShadow: "none", border: "1px #DDDDDD solid", borderRadius: "5px"}}>
            <TableMUI sx={{ minWidth: 650 }} aria-label="table" >
                <TableHead style={{backgroundColor: colors.GRAY_COLOR}}>
                    <TableRow>
                        {columns.map((column) => (
                            <TableCell key={column.name} style={{maxWidth: column.maxWidth, textAlign: "center"}}><Typography>{column.name}</Typography></TableCell>
                        ))}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data && data?.length ? data.map((row, i) => (
                        <TableRow key={i} style={{width: "100%"}}>
                            {columns.map((column) => (
                                <TableCell key={column.name} style={{maxWidth: column.maxWidth,  textAlign: "center"}}>
                                    {column.render ? column.render(row) : row[column.dataIndex]}
                                </TableCell>
                            ))}
                        </TableRow>
                    )) : <TableRow><TableCell colSpan={4}><Typography style={{textAlign: 'center'}} variant="h5">No results found</Typography></TableCell> </TableRow>}
                </TableBody>
            </TableMUI>
        </TableContainer>
    );
};
