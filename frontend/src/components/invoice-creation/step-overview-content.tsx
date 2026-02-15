import React from "react";
import {InvoiceItemTable} from "../invoice/invoice-item-table.tsx";
import {type InvoiceItem, type InvoiceItemCreate, InvoiceType, type Patient} from "../../api";
import {InvoiceCalendar} from "../invoice/invoice-calendar.tsx";
import {Header} from "../header.tsx";
import {InvoicePatientData} from "../invoice/invoice-patient-data.tsx";
import {Total} from "../total.tsx";
import {InvoiceDetails} from "../invoice/invoice-details.tsx";
import {useInvoiceTotal} from "../../hooks/use-invoice-total.ts";

interface StepOverviewProps {
    type: InvoiceType;
    isDraft?: boolean;
    invoiceDate: string;
    invoiceNumber?: string;
    patient: Patient;
    items: InvoiceItemCreate[] | InvoiceItem[];
    dates: Date[];
    diagnosis: string;
    header?: React.ReactNode;
    footer?: React.ReactNode;
    isPreview?: boolean;
}

export const StepOverviewContent: React.FC<StepOverviewProps> = ({
    type, isDraft, invoiceDate, invoiceNumber, patient, items, dates, diagnosis, header, footer, isPreview = false
}) => {
    const isKG = (type === InvoiceType.KG);
    const calculatedTotal = useInvoiceTotal(type, items, dates);

    const displayedItems = React.useMemo(() => {
        if (isKG && isPreview) {
            return [{ quantity: 1, description: 'Anamnese & Befunderhebung', amount: 0.0 }, ...items];
        }
        return items;
    }, [items, isKG, isPreview]);

    return (
        <div className="flex flex-column gap-2">
            {header} {/* Platzhalter für individuellen Header */}

            {isKG && (
                <>
                    <InvoiceCalendar dates={dates} onChange={() => {}}/>
                </>
            )}

            <Header title="Leistungsübersicht"/>
            <InvoiceItemTable invoiceItems={displayedItems} type={type} isLoading={false} />
            <Total total={calculatedTotal}/>

            <Header title="Details"/>
            <InvoiceDetails type={type} isDraft={isDraft} invoiceDate={invoiceDate} invoiceNumber={invoiceNumber} diagnosis={diagnosis}/>

            <Header title="Patientendaten"/>
            <InvoicePatientData patient={patient}/>

            {footer} {/* Platzhalter für individuellen Footer */}
        </div>
    );
};
