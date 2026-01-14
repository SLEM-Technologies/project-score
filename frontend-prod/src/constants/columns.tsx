import {Typography, Autocomplete, TextField, Select} from "../components";
import { Tooltip } from 'react-tooltip'
import React from "react";
import {IPatient} from "../screens/SeacrhClient";

const OPT_OUT_OPTIONS = [
    {label: "Yes", value: true},
    {label: "No", value: false}
]

const formatAge = (age: number): string => {
    if (age === 0) return "< 1 year old";
    if (age === 1) return "1 year old";
    return `${age} years old`;
}

export const columns = (
    outcomes:{label: string, value: string}[],
    changeValue: (value: string, fieldName: string, record: IPatient) => void ) => ([
    {
        name: "Pets",
        dataIndex: "name",
        maxWidth: "50px",
        render: (record: IPatient) => <div data-tooltip-id="name"
                                           data-tooltip-html={`
            ${record.name}<br />
            ${record.species_description ? record.species_description + "</br>" : ""}
            ${record.breed_description ? record.breed_description + "</br>" : ""}
            ${record.gender_description ? record.gender_description + "</br>" : ""}
            ${typeof record.patient_age === 'number' ? (formatAge(record.patient_age))+ "</br>" : ""}
            ${record.odu_id ? record.odu_id : ""}`}
        >
            <Typography noWrap style={{fontWeight: 'bold'}}>{record.name}</Typography>
            {record.species_description ? <Typography noWrap>{record.species_description}</Typography> : null}
            {record.breed_description ? <Typography noWrap>{record.breed_description}</Typography> : null}
            {record.gender_description ? <Typography noWrap>{record.gender_description}</Typography> : null}
            {typeof record.patient_age === 'number'
                ? <Typography noWrap>{formatAge(record.patient_age)}</Typography>
                : null}
            {record.odu_id && <Typography noWrap>{record.odu_id}</Typography>}
            <Tooltip id="name"/>
        </div>
    },
    {
        name: "Reminders due",
        dataIndex: "reminders",
        maxWidth: "50px",
        render: (record: IPatient) => <>
            <Typography data-tooltip-html={`${record.reminders.length ? record.reminders.map(el => `${el.description} - due ${el.date_due}<br />`).join("") : "Not scheduled"}`} sx={{
                display: '-webkit-box',
                WebkitBoxOrient: 'vertical',
                WebkitLineClamp: 6,
                overflow: 'hidden',
            }} style={{whiteSpace: 'pre-line'}} data-tooltip-id="reminders">
                {record.reminders?.length ? record.reminders?.map(el => `${el.description} - due ${el.date_due}\n`) : "Not scheduled"}</Typography>
            <Tooltip id="reminders"/>
        </>
    },
    {
        name: "Last appointment",
        dataIndex: "last_appointment",
        maxWidth: "50px",
        render: (record: IPatient) => <div data-tooltip-id="last_appointment"
                                           data-tooltip-html={`${record.last_appointment?.date || "Not scheduled"}`}
        >
            <Typography noWrap>{record.last_appointment?.date || "Not scheduled"}</Typography>
            <Tooltip id="last_appointment"/>
        </div>
    },
    {
        name: "Next appointment(s)",
        dataIndex: "next_appointments",
        maxWidth: "50px",
        render: (record: IPatient) => <>
            <Typography data-tooltip-html={`${record.next_appointments.length ? record.next_appointments?.map(el => `${el.date}<br />`).join("") : "Not scheduled"}`} sx={{
                display: '-webkit-box',
                WebkitBoxOrient: 'vertical',
                WebkitLineClamp: 4,
                overflow: 'hidden',
            }} style={{whiteSpace: 'pre-line'}} data-tooltip-id="next_appointments">
                {record.next_appointments.length ? record.next_appointments?.map(el => `${el.date}\n`) : "Not scheduled"}
            </Typography>
            <Tooltip id="next_appointments"/>
        </>
    },
    {
        name: "Outcome",
        dataIndex: "outcome",
        maxWidth: "35%",
        render: (record: IPatient) => <Autocomplete options={outcomes} variant="standard" value={record.outcome}
                                    disableClearable onChange={(_e, value: { label: string, value: string }) =>
                                        changeValue(value.value, "outcome", record)}/>
    },
    {
        name: "Save date",
        dataIndex: "outcome_at",
        maxWidth: "50px",
        render: (record: IPatient) => <div data-tooltip-id="outcome_at"
                                           data-tooltip-html={`${record.outcome_at ? new Date(record.outcome_at).toLocaleDateString() : "-"}`}
        >
            <Typography noWrap>{record.outcome_at ? new Date(record.outcome_at).toLocaleDateString() : "-"}</Typography>
            <Tooltip id="outcome_at"/>
        </div>
    },
    {
        maxWidth: "50px",
        name: "Did client opt out?",
        dataIndex: "opt_out",
        render: (record: IPatient) => <Select options={OPT_OUT_OPTIONS} variant="standard"
                                    value={record.opt_out} fullWidth
                                    onChange={(e) =>
                                        changeValue(e.target.value as string, "opt_out", record)}/>
    },
    {
        name: "Additional comments",
        dataIndex: "comment",
        maxWidth: "300px",
        render: (record: IPatient) => <TextField value={record.comment || ""} multiline fullWidth
                                     onChange={(e) => changeValue(e.target.value, "comment", record)}/>
    }
]);
