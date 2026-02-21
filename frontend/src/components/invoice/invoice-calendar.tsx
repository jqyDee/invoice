import {Calendar} from "primereact/calendar";
import React from "react";
import {Header} from "../../utilities/header.tsx";

interface InvoiceCalendarProps {
    dates: Date[];
    onChange: (e: any) => void;
}

export const InvoiceCalendar: React.FC<InvoiceCalendarProps> = ({dates, onChange}) => {
    const dateCount = () => {
        return "(" + dates.length + "/10)"
    }

    return (
        <>
            <Header title={"Behandlungstermine " + dateCount()} />
            <Calendar
                value={dates}
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