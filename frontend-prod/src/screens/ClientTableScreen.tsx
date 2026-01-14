import React, {useEffect, useState} from 'react';
import {Autocomplete, Typography, Table, TextField, Button, DateRangePicker} from "../components";
import {
    Backdrop,
    CircularProgress,
    Container,
    Grid,
    TablePagination,
    MenuItem,
    ListItemText, FormControl} from "@mui/material";
import {contactedColumns} from "../constants/contactedColumns";
import {logout} from "../features/auth/authSlice";
import {checkTokenExpiry} from "../api";
import {useDispatch} from "react-redux";
import {getContactedInfo, switchSMS, getPractices, IContacted, IPractices} from "../api/clients";
import {Checkbox} from "../components";
import {colors} from "../constants";
import {useNavigate} from 'react-router-dom';

const StatusOptions = ["Followed Up", "Not followed Up"];

interface IOptions {
    label: string;
    value: string[];
    type: string;
}

const ClientTableScreen: React.FC = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [data, setData] = useState<IContacted[]>();
    const [page, setPage] = useState<number>(0);
    const [practiceOptions, setPracticeOptions] = useState<IOptions[]>([]);
    const [rowsPerPage, setRowsPerPage] = useState<number>(25);
    const [count, setCount] = useState<number>(0);
    const [status, setStatus] = useState<string[]>(sessionStorage.getItem('status') ? JSON.parse(sessionStorage.getItem('status') as string) : ["Not followed Up"]);
    const [nameFilter, setNameFilter] = useState<string>(sessionStorage.getItem('nameFilter') ? sessionStorage.getItem('nameFilter') as string : '');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [dateRange, setDateRange] = useState<{startDate: string, endDate: string} | undefined>(sessionStorage.getItem('dateRange') ? JSON.parse(sessionStorage.getItem('dateRange') as string) : undefined);
    const [rangeFieldValue, setRangeFieldValue] = useState<string>(sessionStorage.getItem('rangeFieldValue') ? sessionStorage.getItem('rangeFieldValue') as string : '');
    const [practiceFilter, setPracticeFilter] = useState<IOptions[]>(sessionStorage.getItem('practiceFilter') ? JSON.parse(sessionStorage.getItem('practiceFilter') as string) : []);

    const authCheck = async () => {
        const isNotAuth: boolean | undefined = await checkTokenExpiry()
        return isNotAuth;
    }

    const getContactedList = async (limit?: number, offset?: number) => {
        setIsLoading(true);
        const contactedList = await getContactedInfo({
            limit: Number.isInteger(limit) && limit ? limit : rowsPerPage,
            offset: Number.isInteger(offset) && offset !== undefined ? offset * rowsPerPage : page,
            name: nameFilter.length > 2 ? nameFilter : undefined,
            followed: (status.includes("Followed Up") && status.includes("Not followed Up")) || status.length === 0
                ? undefined
                : status.includes("Followed Up"),
            sent_after: dateRange?.startDate ? dateRange?.startDate : undefined,
            sent_before: dateRange?.endDate ? dateRange?.endDate : undefined,
            practice: practiceFilter.length > 0 ? [...new Set(practiceFilter.flatMap((practice) => practice.value))] : undefined
        });
        setData(contactedList.results);
        setCount(contactedList.count)
        setIsLoading(false);
    }

    const getPracticesList = async () => {
        const practices = await getPractices();
        const formattedPractices = formatPractices(practices);
        setPracticeOptions(formattedPractices);
    }

    const formatPractices = (practices: IPractices) => {
        const formattedPractices = Object.keys(practices.mapping).map((key) => {
            return {
                label: key,
                value: practices.mapping[key],
                type: 'practicesGroup'
            }
        });
        const practicesArray = practices.practices.map((practice) => {
            return {
                label: practice.name,
                value: [practice.odu_id],
                type: 'practice'
            }
        });
        return [...formattedPractices, ...practicesArray];
    }

    useEffect(() => {
        const checkAuth = async () => {
            const isNotAuth = await authCheck();
            if (isNotAuth) {
                dispatch(logout());
            }
        };
        checkAuth();
        getContactedList();
        getPracticesList();
    },[])

    const handleChangePage = (newPage: number) => {
        setPage(newPage);
        getContactedList(undefined, newPage);
    }

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
        getContactedList(parseInt(event.target.value, 10));
    }

    const onFilterApply = () => {
        setPage(0)
        getContactedList(undefined, 0);
    }

    const handleCheckboxes = async (sms_id: string) => {
        setIsLoading(true);
        const response = await switchSMS(sms_id);
        if (response.uuid) {
            setData(data?.map((item) => {
                if (item.sms_history_id === sms_id) {
                    return {...item, is_followed: response.is_followed}
                }
                return item;
            }));
        }
        setIsLoading(false);
    }

    const ITEM_HEIGHT = 48;
    const ITEM_PADDING_TOP = 8;
    const MenuProps = {
        PaperProps: {
            style: {
                maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
                width: 250,
                borderColor: colors.PRIMARY_COLOR,
            },
        },
    };

    const handleChange = (event: any) => {
        const {
            target: { value },
        } = event;
        setStatus(
            typeof value === 'string' ? value.split(',') : value,
        );
        sessionStorage.setItem('status', JSON.stringify(typeof value === 'string' ? value.split(',') : value));
    };

    const onReset = () => {
        setStatus(["Followed Up"]);
        setNameFilter('');
        setRangeFieldValue('');
        setDateRange(undefined);
        setPracticeFilter([]);
        sessionStorage.removeItem('status');
        sessionStorage.removeItem('nameFilter');
        sessionStorage.removeItem('rangeFieldValue');
        sessionStorage.removeItem('dateRange');
        sessionStorage.removeItem('practiceFilter');
    }

    const onPracticeChange = (event: any, value: IOptions[], reason: string) => {
        const clickedItem = practiceOptions.find((item) => item.label.split(' ').filter(item => item).join(' ') == event.target.innerText.trim());
        if (clickedItem?.type === 'practicesGroup' && reason === 'selectOption') {
            const practices = practiceOptions.filter((option) => option.type === 'practice');
            const practicesFromGroup = practices.filter((practice) => clickedItem.value.includes(practice.value[0]));
            const uniquePractices = practicesFromGroup.filter((practice) => !practiceFilter.includes(practice));
            setPracticeFilter([clickedItem, ...uniquePractices, ...practiceFilter]);
            sessionStorage.setItem('practiceFilter', JSON.stringify([clickedItem, ...uniquePractices, ...practiceFilter]));
        }
        if (clickedItem?.type === 'practicesGroup' && reason === 'removeOption') {
            const practicesFromGroup = practiceFilter.filter(practice => practice.label !== clickedItem.label).filter((practice) => !clickedItem.value.includes(practice.value[0]));
            setPracticeFilter(practicesFromGroup);
            sessionStorage.setItem('practiceFilter', JSON.stringify(practicesFromGroup));
        }
        if (clickedItem?.type === 'practice' && reason === 'selectOption') {
            setPracticeFilter([...practiceFilter, clickedItem]);
            sessionStorage.setItem('practiceFilter', JSON.stringify([...practiceFilter, clickedItem]));
        }
        if (clickedItem?.type === 'practice' && reason === 'removeOption') {
            const groupPractices = practiceFilter.filter(practice => practice.type === 'practicesGroup');
            const groupPracticesWithoutClicked = groupPractices.filter(practice => !practice.value.includes(clickedItem.value[0]));
            const practices = practiceFilter.filter(practice => practice.label !== clickedItem.label && practice.type === 'practice');
            setPracticeFilter([...groupPracticesWithoutClicked, ...practices]);
            sessionStorage.setItem('practiceFilter', JSON.stringify([...groupPracticesWithoutClicked, ...practices]));
        }
    }

    const onRowClick = (record: IContacted) => {
        navigate('/search-client', {state: {clientId: record.client_id}})
    }

    return (
        <Container maxWidth="xl" style={{justifyContent: 'center', marginBottom: '50px'}}>
            <Grid container justifyContent="space-between" marginTop={2}>
                <Grid item xs={2.5}>
                    <TextField fullWidth margin="normal" name="firstName"
                               label="Search Client Name"
                               variant="outlined"
                               value={nameFilter}
                                    onChange={(e) => setNameFilter(e.target.value)}
                               onBlur={(e) => sessionStorage.setItem('nameFilter', e.target.value)}
                    />
                </Grid>
                <Grid item xs={2.5}>
                    <DateRangePicker
                        setDateRange={(value) =>
                        {
                            setDateRange(value);
                            sessionStorage.setItem('dateRange', JSON.stringify(value));

                        }}
                        inputValue={rangeFieldValue}
                        setInputValue={(value) => {
                            setRangeFieldValue(value);
                            sessionStorage.setItem('rangeFieldValue', value);
                        }}
                    />
                </Grid>
                <Grid item xs={2}>
                    <FormControl fullWidth>
                        <TextField
                            fullWidth
                            label="Status"
                            select
                            variant="outlined"
                            SelectProps={{
                                multiple: true,
                                value: status,
                                onChange: handleChange,
                                renderValue: (selected: any) => selected?.join(', '),
                                MenuProps: MenuProps,
                            }}
                        >
                            {StatusOptions.map((option, index) => (
                                <MenuItem key={index} value={option}>
                                    <ListItemText primary={option} />
                                    <Checkbox checked={status.indexOf(option) > -1} />
                                </MenuItem>
                            ))}
                        </TextField>
                    </FormControl>
                </Grid>
                <Grid item xs={2.5}>
                    <Autocomplete
                        multiple
                        label="Practices"
                        options={practiceOptions}
                        variant="outlined"
                        limitTags={1}
                        disableCloseOnSelect
                        value={practiceFilter}
                        onChange={onPracticeChange}
                        componentsProps={{ clearIndicator: { onClick: () => {
                            setPracticeFilter([])
                                    sessionStorage.removeItem('practiceFilter')
                                } } }}
                        renderTags={(value) => {
                            return (
                                <Typography variant="body2" noWrap style={{width: "50%", color: "black"}}>
                                    {value
                                        .slice(0, 1)
                                        .map((option) => option.label)
                                        .join(", ")}
                                </Typography>
                            );
                        }}
                        getOptionLabel={(option) => option.label}
                        renderOption={(props, option, { selected }) => (
                            <li style={{display: 'flex', justifyContent: 'space-between'}} {...props}>
                                {option.label}
                                <Checkbox
                                    disabled
                                    checked={selected}
                                />
                            </li>
                        )}
                    />
                </Grid>
                <Grid item xs={1}>
                    <Button variant="contained" fullWidth color="primary" onClick={onFilterApply}>Search</Button>
                </Grid>
                <Grid item xs={1}>
                    <Button variant="outlined" fullWidth color="secondary" onClick={onReset}>Reset</Button>
                </Grid>
            </Grid>
            <Grid container alignItems="center" marginTop={3}>
                <Table data={data} columns={contactedColumns(handleCheckboxes, onRowClick)}/>
                <TablePagination
                    component="div"
                    count={count}
                    page={page}
                    onPageChange={(e, page) => handleChangePage(page)}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={(e) => handleChangeRowsPerPage(e)}
                    rowsPerPageOptions={[10, 25, 50, 100]}
                />
            </Grid>
            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                open={isLoading}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
        </Container>
    );
}
export default ClientTableScreen;
