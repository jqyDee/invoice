import React, {useMemo} from "react";
import {InvoiceItemTable} from "../invoice/invoice-item-table.tsx";
import {
    type Invoice,
    type InvoiceCreate, InvoiceType, type InvoiceUpdate
} from "../../api";
import {InvoiceCalendar} from "../invoice/invoice-calendar.tsx";
import {Header} from "../../utilities/header.tsx";
import {InvoicePatientData} from "../invoice/invoice-patient-data.tsx";
import {Total} from "../../utilities/total.tsx";
import {InvoiceDetails} from "../invoice/invoice-details.tsx";
import {useInvoiceTotal} from "../../hooks/invoice/use-invoice-total.ts";
import {useQuery} from "@tanstack/react-query";
import {
    getPatientsPatientsGetOptions
} from "../../api/@tanstack/react-query.gen.ts";
import {enforceNonNull} from "../../utilities/enforce-non-null.ts";

interface StepOverviewProps {
    invoice: Invoice | InvoiceCreate | InvoiceUpdate;
    header?: React.ReactNode;
    footer?: React.ReactNode;
}

export const StepOverviewContent: React.FC<StepOverviewProps> = ({invoice, header, footer}) => {
    const isKG = (invoice.type === InvoiceType.KG);

    const { data: patients } = useQuery(getPatientsPatientsGetOptions());
    const selectedPatient = patients?.find(p => p.patient_id === invoice.patient_id);

    const datesAsDates = useMemo(() =>
        invoice.dates?.map(d => new Date(d.date)) || [],
    [invoice.dates]);

    const calculatedTotal = useInvoiceTotal(
        enforceNonNull(invoice.type),
        enforceNonNull(invoice.user_items),
        datesAsDates
    );

    return (
        <div className="flex flex-column gap-2">
            {header}

            {isKG && (
                <InvoiceCalendar dates={datesAsDates} onChange={() => {}}/>
            )}

            <Header title="Leistungsübersicht"/>
            <InvoiceItemTable invoice={invoice} onChange={() => {}} readonly={true}/>
            <Total total={calculatedTotal}/>

            <Header title="Details"/>
            <InvoiceDetails invoice={invoice} />

            <Header title="Patientendaten"/>
            <InvoicePatientData patient={selectedPatient}/>

            {footer}
        </div>
    );
};
