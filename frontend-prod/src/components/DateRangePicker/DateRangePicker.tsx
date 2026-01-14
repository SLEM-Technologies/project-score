import React from "react";
import {TextField} from "../TextField";
import {
    Popover,
    InputAdornment,
    IconButton
} from "@mui/material";
import moment from "moment";
import {ClearIconSVG} from "../../assets/ClearIconSVG";
import { DateRange } from "react-date-range";
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';
import {colors} from "../../constants";

interface IDateRangePickerProps {
    setDateRange: (DateRange: IDateRange) => void;
    inputValue: string;
    setInputValue: (inputValue: string) => void;
}

interface IDateRange {
    startDate: string;
    endDate: string;
}

export const DateRangePicker = ({setDateRange, inputValue, setInputValue}: IDateRangePickerProps) => {
    const dateFormat = "DD MMM YYYY";
    const [displayCalendar, setDisplayCalendar] = React.useState(false);
    const [anchorEl, setAnchorEl] = React.useState(null);
    const [fromDate, setFromDate] = React.useState<Date>(new Date());
    const [toDate, setToDate] = React.useState<Date>(new Date());

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const onAdornmentClick = e => {
        setDisplayCalendar(true);
        setAnchorEl(e.currentTarget);
    };

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const onPopoverClose = (e, reason) => {
        setDisplayCalendar(false);
        setAnchorEl(null);
    };

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const onSelectDateRanges = ({ selection }) => {
        let { startDate, endDate } = selection;
        startDate = moment(startDate);
        startDate = startDate.isValid() ? startDate.toDate() : undefined;
        endDate = moment(endDate);
        endDate = endDate.isValid() ? endDate.toDate() : undefined;
        let inputValue = "";
        if (startDate) inputValue += moment(startDate).format(dateFormat);
        if (endDate) inputValue += " - " + moment(endDate).format(dateFormat);
        setFromDate(startDate);
        setToDate(endDate);
        setDateRange({ startDate: moment(startDate).format("YYYY-MM-DD"), endDate: moment(endDate).format("YYYY-MM-DD") });
        setInputValue(inputValue);
    };

    const processInputValue = (value: any) => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        let [fromDate, toDate] = value.split("-").map(elm => elm.trim());
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        fromDate = moment(fromDate, dateFormat);
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        fromDate = fromDate.isValid() ? fromDate.toDate() : undefined;
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        toDate = moment(toDate, dateFormat);
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        toDate = toDate.isValid() ? toDate.toDate() : undefined;
        return { fromDate, toDate };
    }

    const clearDateRange = () => {
        setInputValue("");
        setDateRange({ startDate: "", endDate: "" });
        setFromDate(new Date());
        setToDate(new Date());
    }
        return (
            <div>
                <TextField
                    label="Date SMS sent"
                    fullWidth
                    variant={"outlined"}
                    onClick={onAdornmentClick}
                    value={inputValue}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={clearDateRange}>
                                    <ClearIconSVG/>
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />
                <Popover
                    open={displayCalendar}
                    anchorEl={anchorEl}
                    anchorOrigin={{
                        vertical: "bottom",
                        horizontal: "left"
                    }}
                    transformOrigin={{
                        vertical: "top",
                        horizontal: "left"
                    }}
                    onClose={onPopoverClose}
                >
                    <div >
                        <DateRange
                            ranges={[
                                {
                                    startDate: fromDate,
                                    endDate: toDate,
                                    key: "selection"
                                }
                            ]}
                            showPreview={false}
                            rangeColors={[colors.PRIMARY_COLOR]}
                            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                            // @ts-ignore
                            onChange={onSelectDateRanges}
                            maxDate={new Date()}
                            showMonthAndYearPickers={true}
                            moveRangeOnFirstSelection={false}
                            showDateDisplay={false}
                            showSelectionPreview={false}
                            scroll={{ enabled: true }}
                        />
                    </div>
                </Popover>
            </div>
        );
    }

