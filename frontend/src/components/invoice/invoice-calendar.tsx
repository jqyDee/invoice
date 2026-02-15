import {Calendar} from "primereact/calendar";
import React from "react";

interface InvoiceCalendarProps {
    dates: Date[];
    onChange: (e: any) => void;
}

export const InvoiceCalendar: React.FC<InvoiceCalendarProps> = ({dates, onChange}) => {
    return (
        <Calendar
            value={dates}
            onChange={onChange}
            selectionMode="multiple"
            maxDateCount={10}
            inline
            showWeek
            className="w-full"
        />
    )
}