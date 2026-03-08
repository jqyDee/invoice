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
    getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions,
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

    const { data: availableDefaults } = useQuery(
        getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({ query: { invoice_type: invoice.type } })
    );
    const defaultItems = 'invoice_id' in invoice
        ? invoice.default_items
        : (availableDefaults || []).filter(d => invoice.default_item_ids?.includes(d.default_item_id));

    const isSavedInvoice = 'invoice_id' in invoice;
    const userItems = (!isKG && !isSavedInvoice)
        ? (invoice.dates || []).flatMap((d: any) => d.items || [])
        : (invoice.user_items || []);

    const calculatedTotal = useInvoiceTotal(
        [...userItems, ...defaultItems],
        datesAsDates,
        enforceNonNull(invoice.type)
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
