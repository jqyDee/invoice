import {Calendar} from "primereact/calendar";
import type {FormEvent} from "primereact/ts-helpers";
import React from "react";
import {Header} from "../../utilities/header.tsx";

interface InvoiceCalendarProps {
    dates: Date[];
    onChange: (e: FormEvent<Date[]>) => void;
}

export const InvoiceCalendar: React.FC<InvoiceCalendarProps> = ({dates, onChange}) => {
    return (
        <>
            <Header title={`Behandlungstermine (${dates.length}/10)`}/>
            <Calendar
                value={dates}
                showButtonBar
                onChange={onChange}
                selectionMode="multiple"
                maxDateCount={10}
                inline
                showWeek
                className="w-full"
            />
        </>
    )
}