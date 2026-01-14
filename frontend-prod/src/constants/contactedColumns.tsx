import {Typography, Checkbox} from "../components";
import { Tooltip } from 'react-tooltip'
import React from "react";
import moment from "moment";
import {IContacted} from "../api/clients";

const formatPhoneNumber = (phoneNumberString: string | undefined) => {
    const cleaned = ('' + phoneNumberString).replace(/\D/g, '')
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3]
    }
    else return null;
}

export const contactedColumns = (onChange: (id: string) => void, onRowClick: (record: IContacted) => void) => ([
    {
        name: "Client Contacted",
        dataIndex: "name",
        maxWidth: "50px",
        render: (record: IContacted) => <div data-tooltip-id="name" data-tooltip-html={`
            ${record.full_name}<br />
            ${record?.emails.length ? record?.emails[0]?.address + "</br>" : ""}
            ${record.phones.length ? formatPhoneNumber(record.phones[0].app_number) + "</br>" : ""}
            ${record.patients ? record.patients.map(pet => pet.name).join(", ") : ""}
`} onClick={() => onRowClick(record)}>
            <div style={{display: "flex", cursor: 'pointer'}}>
                <Typography style={{fontWeight: 'bold'}}>Client:</Typography>
                <Typography noWrap style={{marginLeft: "5px"}}>{record.full_name}</Typography>
            </div>
            {record?.emails.length ? <div style={{display: "flex", cursor: 'pointer'}}>
                <Typography style={{fontWeight: 'bold'}}>Email:</Typography>
                <Typography noWrap style={{marginLeft: "5px"}}>{record?.emails.length ? record?.emails[0]?.address : "-"}</Typography>
            </div> : null}
            {record.phones.length ? <div style={{display: "flex", cursor: 'pointer'}}>
                <Typography style={{fontWeight: 'bold'}}>Phone number:</Typography>
                <Typography noWrap style={{marginLeft: "5px"}}>{record.phones.length ? formatPhoneNumber(record.phones[0].app_number) : "-"}</Typography>
            </div> : null}
            {record.patients ? <div style={{display: "flex", cursor: 'pointer'}}>
                <Typography style={{fontWeight: 'bold'}}>Pet(s):</Typography>
                <Typography noWrap style={{marginLeft: "5px"}}>{
                    record.patients?.map(pet => pet.name).join(", ")
                }</Typography>
            </div> : null}
            <Tooltip id="name"/>
        </div>
    },
    {
        name: "Practice Name",
        dataIndex: "reminders",
        maxWidth: "50px",
        render: (record: IContacted) => <div onClick={() => onRowClick(record)} style={{cursor: 'pointer'}}>
            <Typography data-tooltip-html={`${record.practice_name}`} data-tooltip-id="practice">
                {record.practice_name}</Typography>
            <Tooltip id="practice"/>
        </div>
    },
    {
        name: "Date SMS sent",
        dataIndex: "sms_date",
        maxWidth: "50px",
        render: (record: IContacted) => <div data-tooltip-id="sms_date"
                                           data-tooltip-html={`${record.sent_at ? moment(record.sent_at).format('YYYY-MM-DD') : "-"}`}
                                             onClick={() => onRowClick(record)}
                                             style={{cursor: 'pointer'}}
        >
            <Typography noWrap>{record.sent_at ? moment(record.sent_at).format('YYYY-MM-DD') : "-"}</Typography>
            <Tooltip id="sms_date"/>
        </div>
    },
    {
        name: "Followed up",
        dataIndex: "next_appointments",
        maxWidth: "50px",
        render: (record: IContacted) => <>
            <Checkbox
                onChange={() => onChange(record.sms_history_id)}
                checked={record.is_followed}/>
        </>
    },
]);
