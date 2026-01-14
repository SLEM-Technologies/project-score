import React, {useState, useRef, useEffect} from 'react';
import {Button, TextField, Typography, RadioButton, Autocomplete, Table, Select} from "../components";
import {useLocation} from 'react-router-dom';
import {Backdrop, CircularProgress, Container, Grid, Modal, Box} from '@mui/material';
import {
    getClients,
    IClientsList,
    getClientInfo,
    checkTokenExpiry,
    getOutcomes,
    updateClient,
    getFAQ,
    IPhone, IEmail
} from "../api";
import {colors} from "../constants";
import {useSnackbar} from "notistack";
import {columns} from "../constants/columns";
import {useDispatch} from "react-redux";
import {logout} from "../features/auth/authSlice";

export interface SearchFormValues {
    odu_id: string,
    first_name: string,
    last_name: string,
    full_name?: string,
    email_address: string | null,
    email_id?: string | null,
    phone_id?: string | null,
    phone_number: string | null,
    practice_name: string | null,
    patients?: IPatient[]
}

export interface IPatient {
    "odu_id": string,
    "species_description": string,
    "breed_description": string,
    "gender_description": string,
    "name": string,
    "patient_age": number | null,
    "outcome": null | string,
    "opt_out": null | string,
    "comment": null | string,
    "reminders": IReminders[],
    "last_appointment": {
        date?: string
    },
    "next_appointments": {date: string}[],
    "outcome_at"?: Date,
    [key: string]: any
}

interface IReminders {
    "date_due": string,
    "description": string,
    "sms_status": string
}

const init = {
    first_name: '',
    last_name: '',
    phone_number: '',
    email_address: '',
    odu_id: '',
    practice_name: '',
}

const style = {
    position: 'absolute' as const,
    top: '50%',
    left: '50%',
    minWidth: "650px",
    transform: 'translate(-50%, -50%)',
    bgcolor: 'background.paper',
    border: `2px solid ${colors.PRIMARY_COLOR}`,
    borderRadius: "6px",
    p: 4,
};


const fieldsLabels = {
    first_name: "First Name",
    last_name: "Last Name",
    email_address: "Email",
    phone_number: "Phone",
}

const SearchClientScreen: React.FC = () => {
    const dispatch = useDispatch();
    const location = useLocation();
    const { enqueueSnackbar } = useSnackbar();
    const autocompleteRef = useRef<any>();
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const [open, setOpen] = useState(false);
    const [searchType, setSearchType] = useState<string>("searchName");
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [searchingPhone, setSearchingPhone] = useState("");
    const [searchingParams, setSearchingParams] = useState("");
    const [clientsList, setClientsList] = useState<{label: string, value: string}[]>([]);
    const [values, setValues] = useState<SearchFormValues>(init);
    const [initValues, setInitValues] = useState<SearchFormValues>(init);
    const [inputValue, setInputValue] = React.useState('')
    const [outcomesList, setOutComesList] = useState<{label: string, value: string}[]>([]);
    const [practiceList, setPracticeList] = useState<{label: string, value: string}[]>([]);
    const [selectedPractice, setSelectedPractice] = useState<string>("");
    const [questions, setQuestions] = useState<{label: string, value: string}[]>([]);
    const [selectedQuestions, setSelectedQuestions] = useState<string>("");
    const [phonesList, setPhonesList] = useState<IPhone[]>([]);
    const [emailsList, setEmailsList] = useState<IEmail[]>([]);

    const compareObjects = () => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        return Object.keys(values).every(key => values[key] === initValues[key])
    }

    useEffect( () => {
        getFAQList();
    },[selectedPractice])

    useEffect(() => {
        const clientId = location.state?.clientId;
        if (clientId) {
            onClientSelect(clientId);
        }
    },[])

    useEffect(() => {
        const checkAuth = async () => {
            const isNotAuth = await authCheck();
            if (isNotAuth) {
                dispatch(logout());
            }
        };
        checkAuth();
        getOutcomesList();
    },[])

    const getFAQList = async () => {
        if (selectedPractice) {
            const FAQ = await getFAQ(selectedPractice);
            setQuestions(FAQ.map((el) => ({value: el.answer, label: el.question})))
        }
    }

    const getOutcomesList = async () => {
        const response = await getOutcomes();
        setOutComesList(response.map(el => ({label: el, value: el})))
    }

    const authCheck = async () => {
        const isNotAuth: boolean | undefined = await checkTokenExpiry()
        return isNotAuth;
    }

    const formatPhoneNumber = (phoneNumberString: string | undefined) => {
        const cleaned = ('' + phoneNumberString).replace(/\D/g, '')
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
        if (match) {
            return '(' + match[1] + ') ' + match[2] + '-' + match[3]
        }
        else return null;
    }

    const clientsListFormatter = (data: IClientsList[]) => {
        return data.map(el => (
            {
                value: el.odu_id,
                label: `[${el.odu_id}] - ${el.full_name}${el.email_address ? 
                    (" - " + el.email_address) : ""}${el.phone_number ? (" - " + formatPhoneNumber(el.phone_number)) : ""}`,
            }
        ))
    }

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.value.length < 255) {
            setValues({
                ...values,
                [event.target.name]: event.target.value,
            });
        }
    };

    const onClientSelect = async (id: string) => {
        try {
            setIsLoading(true);
            const isNotAuth = await authCheck()
            if(isNotAuth) {
                dispatch(logout());
                return;
            }
            await getClient(id);
        }
        catch (error) {
            console.log(error)
        }
        finally {
            setIsLoading(false);
        }
    }

    const getClient = async (id: string) => {
        const personalInfo = await getClientInfo(id);
        setValues({...personalInfo,
            email_address: personalInfo.emails.length === 1 ? personalInfo.emails[0]?.address : "",
            phone_number: personalInfo.phones.length === 1 ? formatPhoneNumber(personalInfo.phones[0]?.app_number) : "",
            email_id: personalInfo.emails.length === 1 ? personalInfo.emails[0]?.odu_id : null,
            phone_id: personalInfo.phones.length === 1 ? personalInfo.phones[0]?.odu_id : null,
            practice_name: personalInfo.practices.length ? personalInfo.practices[0].name : "",
        });
        setInitValues({...personalInfo,
            email_address: personalInfo.emails.length === 1 ? personalInfo.emails[0]?.address : "",
            phone_number: personalInfo.phones.length === 1 ? formatPhoneNumber(personalInfo.phones[0].app_number) : "",
            email_id: personalInfo.emails.length === 1 ? personalInfo.emails[0]?.odu_id : null,
            phone_id: personalInfo.phones.length === 1 ? personalInfo.phones[0]?.odu_id : null,
            practice_name: personalInfo.practices.length ? personalInfo.practices[0].name : "",
        });
        if (personalInfo.phones.length > 1) {
            setPhonesList(personalInfo.phones)
        }
        else {
            setPhonesList([]);
        }
        if (personalInfo.emails.length > 1) {
            setEmailsList(personalInfo.emails)
        }
        else {
            setEmailsList([]);
        }
        setPracticeList(personalInfo.practices.map((el) => ({label: el.name, value: el.odu_id})));
        setSelectedPractice(personalInfo.practices[0].odu_id);
        setSelectedQuestions("");
    }

    const clearPhone = (phone: string) => {
        return phone?.replace(/[()-\s]/g, "");
    }


    const handleSearch = async (withValidation?: boolean) => {
        try {
            if (withValidation && !compareObjects()) {
                setIsModalOpen(true);
                return;
            }
            setIsLoading(true);
            const isNotAuth = await authCheck()
            if(isNotAuth) {
                dispatch(logout());
                return;
            }
            const phone = clearPhone(searchingPhone);
            if (searchType === "searchPhone" && phone.length !== 10) {
                enqueueSnackbar('10 digits are required to get search results', { variant: 'error' });
                return;
            }
            if (searchType === "searchName" && searchingParams.length < 3) {
                enqueueSnackbar('At least 3 entered symbols are required to get search results', { variant: 'error' });
                return;
            }
            const data = await getClients(
                {search: searchingParams, phone_number: phone});
            if (data.length > 1) {
                setClientsList(clientsListFormatter(data));
                setInputValue(searchingParams);
                setOpen(true);
                autocompleteRef.current.focus();
            }
            else if (data.length === 1) {
                await getClient(data[0].odu_id);
                setClientsList([]);
            }
            else {
                enqueueSnackbar('No results found. Please refine your search and try again.', { variant: 'error' });
                setClientsList([]);
                setValues(init);
                setInputValue("");
                setSelectedQuestions("");
                setSelectedPractice("");
                setPhonesList([]);
                setEmailsList([]);
            }
        }
        catch (error) {
            enqueueSnackbar('Something went wrong', { variant: 'error' });
        }
        finally {
            setIsLoading(false);
        }
    }

    const updateSearchType = (type: string) => {
        setSearchingPhone("");
        setSearchingParams("");
        setSearchType(type);
    }

    const onPatientChange = (value: string, fieldName: string, record: IPatient) => {
        if (value?.length < 1001 || typeof value === 'boolean') {
            const patients = values.patients?.map(el => {
                if (el.odu_id === record.odu_id) {
                    if (fieldName === "outcome") {
                        return {
                            ...el,
                            [fieldName]: value,
                            outcome_at: new Date(),
                        }
                    }
                    else {
                        return {
                            ...el,
                            [fieldName]: value,
                        }
                    }
                }
                return el;
            })
            setValues({...values, patients});
        }
    }

    const onCancel = () => {
        setValues(initValues);
    }

    const checkRequiredFields = () => {
        const requiredFields = ["first_name", "last_name", "phone_number", "email_address"];
        const emptyFields: string[] = [];
        requiredFields.forEach(el => {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            if (!values[el] || (el === "phone_number" && values[el]?.length !== 14)) {
                // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                // @ts-ignore
                emptyFields.push(fieldsLabels[el]);
            }
        })
        return emptyFields.join(", ");
    }

    const formatPatientsData = (originalArray: IPatient[], updatedArray: IPatient[]): IPatient[] => {
        const changedObjects: any = [];
        updatedArray.forEach(updatedObj => {
            const originalObj = originalArray.find(obj => obj.odu_id === updatedObj.odu_id);
            if (originalObj) {
                const changedFields: { [key: string]: any } = {};
                for (const key in updatedObj) {
                    if (updatedObj[key] !== originalObj[key]) {
                        console.log(updatedObj[key]);
                        changedFields[key] = updatedObj[key].toString().length ? updatedObj[key] : null;
                    }
                }
                if (Object.keys(changedFields).length > 0) {
                    changedObjects.push({
                        odu_id: updatedObj.odu_id,
                        ...changedFields
                    });
                }
            }
        });
        return changedObjects;
    }

    const onSave = async () => {
        try {
            setIsLoading(true);
            if (!values.first_name || !values.last_name || (!values.email_address && initValues.email_address?.length) || values.phone_number?.length !== 14) {
                enqueueSnackbar(`Please fill in ${checkRequiredFields()}`, { variant: 'error' });
                return;
            }
            const data = await updateClient(values.odu_id,
                {
                        first_name: initValues.first_name !== values.first_name ? values.first_name : undefined,
                        last_name: initValues.last_name !== values.last_name ? values.last_name : undefined,
                        email: values.email_address !== initValues.email_address && values.email_address ? values.email_id
                            ? emailsList.find(el => el.address === values.email_address) ?
                                {odu_id: values.email_id, set_is_primary: true} :
                                {address: values.email_address, odu_id: values.email_id, set_is_primary: true}
                            : {address: values.email_address || null} : undefined,
                        phone: values.phone_number !== initValues.phone_number ? values.phone_id
                            ? phonesList.find(el => el.app_number === clearPhone(values.phone_number ? values.phone_number : "")) ?
                                {odu_id: values.phone_id, set_is_primary: true } :
                                {app_number: clearPhone(values.phone_number), odu_id: values.phone_id, set_is_primary: true }
                            : {app_number: clearPhone(values.phone_number)} : undefined,
                        patients: formatPatientsData(initValues?.patients || [], values?.patients || [])
                    }
            );
            if (data) {
                setInitValues(values);
                enqueueSnackbar('Changes saved!', { variant: 'success' });
            }
            else {
                enqueueSnackbar('Something went wrong', { variant: 'error' });
            }
        }
        catch (error) {
            enqueueSnackbar('Something went wrong', { variant: 'error' });
        }
        finally {
            setIsLoading(false);
            setIsModalOpen(false);
        }
    }

     const handleBeforeUnload = (e: BeforeUnloadEvent) => {
        e.preventDefault();
        e.returnValue = '';
     }

     useEffect(() => {
        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        }
     })

    const onContinue = async () => {
        setIsModalOpen(false);
        await setValues(init);
        await setInitValues(init);
        await handleSearch(false);
    }


    return (
        <Container maxWidth="xl" style={{justifyContent: 'center', marginBottom: '50px'}}>
            <Grid container>
                <Grid item xs={8} paddingRight="40px">
                    <Typography variant="h5" component="h1" fontWeight={600}>
                        Search clients
                    </Typography>
                    <RadioButton label="Search by client ID, full name, or email" name={"searchName"}
                                 onChange={(event) =>
                                     updateSearchType(event.target.name)} checked={searchType === "searchName"}
                    />
                    <RadioButton label="Search by phone number" name={"searchPhone"}
                                 onChange={(event) =>
                                     updateSearchType(event.target.name)} checked={searchType === "searchPhone"}
                    />
                    <Grid container justifyContent="space-between" marginTop={2}>
                        <Grid item xs={9}>
                            {searchType === "searchName" ?
                                <TextField fullWidth margin="normal" name="firstName"
                                           onKeyDown={e => e.key === "Enter" ? handleSearch(true) : null}
                                    label="Search by client ID, full name, or email"
                                    variant="outlined" value={searchingParams}
                                           onChange={(event) => setSearchingParams(event.target.value)}
                                /> :
                                <TextField fullWidth margin="normal" name="searchingPhone" label="Search by Phone number"
                                           onKeyDown={e => e.key === "Enter" ? handleSearch(true) : null}
                                    variant="outlined" type="tel" value={searchingPhone} onChange={(event) => {
                                        setSearchingPhone(event.target.value)
                                    }}
                                />
                            }
                        </Grid>
                        <Grid item>
                            <Button variant="contained" type='submit' color="primary" onClick={() => handleSearch(true)}>
                                Search
                            </Button>
                        </Grid>
                    </Grid>
                    <Grid container marginTop={2}>
                        <Grid item xs={9}>
                            <Autocomplete
                                options={clientsList} variant="outlined" label="Clients"
                                disabled={clientsList.length <= 1}
                                onChange={(_event, value: { label: string, value: string }) => {
                                    onClientSelect(value.value)
                                }}
                                inputValue={inputValue}
                                onInputChange={(_, newInputValue) => {
                                    setInputValue(newInputValue)
                                }}
                                disableClearable
                                open={open}
                                onOpen={() => setOpen(true)}
                                onClose={() => setOpen(false)}
                                autocompleteRef={autocompleteRef}
                                ref={autocompleteRef}
                            />
                        </Grid>
                    </Grid>
                    <Grid container alignItems="center" marginTop={5}>
                        <Grid item xs={2}>
                            <Typography>First Name</Typography>
                        </Grid>
                        <Grid item xs={10}>
                            <TextField fullWidth margin="normal" name="first_name" variant="outlined" inputProps={{maxLength: 12}}
                                       disabled={!values.odu_id} value={values.first_name} onChange={handleChange}
                            />
                        </Grid>
                    </Grid>
                    <Grid container alignItems="center" marginTop={3}>
                        <Grid item xs={2}>
                            <Typography>Last Name</Typography>
                        </Grid>
                        <Grid item xs={10}>
                            <TextField fullWidth margin="normal" name="last_name" variant="outlined" value={values.last_name}
                                       disabled={!values.odu_id} onChange={handleChange}
                            />
                        </Grid>
                    </Grid>
                    <Grid container alignItems="center" marginTop={3}>
                        <Grid item xs={2}>
                            <Typography>Phone</Typography>
                        </Grid>
                        <Grid item xs={10}>
                            <TextField fullWidth margin="normal" name="phone_number" type="tel" variant="outlined" value={values.phone_number}
                                       disabled={!values.odu_id} onChange={handleChange}
                            />
                            {!!phonesList.length && <>
                                <Typography>{`It looks like we have ${phonesList.length} phone numbers for ${values.full_name}. Please select the most up-to-date one.`}</Typography>
                                {phonesList.map((phone, index) =>
                                    <RadioButton label={formatPhoneNumber(phone.app_number) || undefined}
                                                 key={index} checked={values.phone_id === phone.odu_id}
                                                 onChange={() => setValues({...values, phone_number: formatPhoneNumber(phone.app_number), phone_id: phone.odu_id })}
                                />)}
                            </>}
                        </Grid>
                    </Grid>
                    <Grid container alignItems="center" marginTop={3}>
                        <Grid item xs={2}>
                            <Typography>Email</Typography>
                        </Grid>
                        <Grid item xs={10}>
                            <TextField fullWidth margin="normal" name="email_address" variant="outlined" value={values.email_address}
                                       disabled={!values.odu_id} onChange={handleChange}
                            />
                            {!!emailsList.length && <>
                                <Typography>{`It looks like we have ${emailsList.length} emails for ${values.full_name}. Please select the most up-to-date one.`}</Typography>
                                {emailsList.map((email, index) =>
                                    <RadioButton label={email.address}
                                                 key={index} checked={values.email_id === email.odu_id}
                                                 onChange={() => setValues({...values, email_address: email.address, email_id: email.odu_id })}
                                    />)}
                            </>}
                        </Grid>
                    </Grid>
                    <Grid container alignItems="center" marginTop={3}>
                        <Grid item xs={2}>
                            <Typography>Client ID</Typography>
                        </Grid>
                        <Grid item xs={10}>
                            <TextField fullWidth margin="normal" name="odu_id" variant="outlined" value={values.odu_id}
                                       disabled onChange={handleChange}
                            />
                        </Grid>
                    </Grid>
                    <Grid container alignItems="center" marginTop={3}>
                        <Grid item xs={2}>
                            <Typography>Practice</Typography>
                        </Grid>
                        <Grid item xs={10}>
                            <TextField fullWidth margin="normal" name="practice" variant="outlined" value={values.practice_name} multiline
                                       disabled onChange={handleChange}
                            />
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={4}>
                    <Typography variant="h5" fontWeight={600}>
                        Search Practice Specific Questions
                    </Typography>
                    <Grid container marginTop="48px">
                        <Select
                            variant="outlined"
                            label="Practice Name"
                            options={practiceList}
                            value={selectedPractice}
                            disabled={practiceList.length <= 1}
                            onChange={(e) => setSelectedPractice(e.target.value as string)}
                            fullWidth
                        />
                    </Grid>
                    <Grid container marginTop={2}>
                        <Autocomplete
                            options={questions} variant="outlined" label="Search Practice Specific Questions"
                            disabled={!selectedPractice || !questions.length}
                            onChange={(_event, value: { label: string, value: string }) => {
                                setSelectedQuestions(value.value)
                            }}
                            disableClearable
                            value={selectedQuestions}
                            fullWidth
                        />
                    </Grid>
                    <Grid style={{overflowY: "auto", overflowX: "hidden"}} marginTop={2} border={`1px solid ${colors.PRIMARY_COLOR}`} borderRadius="5px" padding="16px 12px" maxHeight="480px" overflow="scroll">
                        <Typography variant="body1" style={{whiteSpace: 'pre-wrap', wordWrap: 'break-word', display: "block", overflowWrap: 'break-word'}}>{values.odu_id ? (practiceList.length ? selectedQuestions.replace("\r\n", "\n") || "No results provided by the practice" : "Results will show once a practice is added" ) : "Results will show once a client is selected"}</Typography>
                    </Grid>
                </Grid>
                {values.patients && values.patients.length ? <Grid container alignItems="center" marginTop={3}>
                    <Table data={values.patients} columns={columns(outcomesList, onPatientChange)}/>
                </Grid> : null}
                {values.odu_id && <Grid container alignItems="center" marginTop={3} justifyContent="space-around">
                    <Grid item xs={6}>
                        <Button variant="outlined" color="secondary" onClick={onCancel}>Cancel Changes</Button>
                    </Grid>
                    <Grid item xs={6}>
                        <Button variant="contained" color="primary" onClick={onSave}>Save Changes</Button>
                    </Grid>
                </Grid>}
            </Grid>
            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                open={isLoading}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
            <Modal open={isModalOpen} onClose={() => setIsModalOpen(false)}>
                <Box sx={style}>
                    <Typography textAlign="center" variant="h5" component="h2">
                        Your changes have not been saved
                    </Typography>
                    <Typography textAlign="center" sx={{ mt: 2 }}>
                        Before you navigate away from this page, would you like to save the changes that you made?
                    </Typography>
                    <Grid container marginTop={3}>
                        <Grid item xs={6} justifyContent="space-around">
                            <Button variant="outlined" color="secondary" onClick={onSave}>Yes, save changes</Button>
                        </Grid>
                        <Grid item xs={6}>
                            <Button variant="contained" color="primary" onClick={onContinue}>No, don’t save changes</Button>
                        </Grid>
                    </Grid>
                </Box>
            </Modal>
        </Container>
    );
};

export default SearchClientScreen;
