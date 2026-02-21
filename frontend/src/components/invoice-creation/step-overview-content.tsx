import React, {useMemo} from "react";
import {InvoiceItemTable} from "../invoice/invoice-item-table.tsx";
import {
    type InvoiceCreate, type InvoiceItemCreate, InvoiceType, type InvoiceUpdate
} from "../../api";
import {InvoiceCalendar} from "../invoice/invoice-calendar.tsx";
import {Header} from "../../utilities/header.tsx";
import {InvoicePatientData} from "../invoice/invoice-patient-data.tsx";
import {Total} from "../../utilities/total.tsx";
import {InvoiceDetails} from "../invoice/invoice-details.tsx";
import {useInvoiceTotal} from "../../hooks/use-invoice-total.ts";
import {useQuery} from "@tanstack/react-query";
import {
    getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions,
    getPatientsPatientsGetOptions
} from "../../api/@tanstack/react-query.gen.ts";
import {enforceNonNull} from "../../utilities/enforce-non-null.ts";

interface StepOverviewProps {
    invoice: InvoiceCreate | InvoiceUpdate;
    header?: React.ReactNode;
    footer?: React.ReactNode;
}

export const StepOverviewContent: React.FC<StepOverviewProps> = ({invoice, header, footer}) => {
    const isKG = (invoice.type === InvoiceType.KG);

    const { data: patients } = useQuery(getPatientsPatientsGetOptions());
    const selectedPatient = patients?.find(p => p.patient_id === invoice.patient_id);

    // 2. Fetch default items to map IDs back to full objects for display
    const { data: allDefaults } = useQuery(getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
        query: { invoice_type: invoice.type }
    }));

    const displayItems = useMemo(() => {
        if (!allDefaults) return invoice.user_items || [];

        const activeDefaults = allDefaults.filter(d =>
            invoice.default_item_ids?.includes(d.default_item_id)
        );

        const prepend = activeDefaults.filter(d =>
            d.position === "PREPEND" || d.position === "BOTH"
        );
        const append = activeDefaults.filter(d =>
            d.position === "APPEND" || d.position === "BOTH"
        );

        return [...prepend, ...(invoice.user_items || []), ...append];
    }, [invoice, allDefaults]);

    const standardizedItems: InvoiceItemCreate[] = displayItems.map((item) => {
        const dateCount = invoice.dates?.length || 1;
        return {
            description: item.description,
            amount: item.amount,
            // Use date multiplier if quantity is null
            quantity: item.quantity ?? (isKG ? dateCount : 1),
            number: item.number ?? null,
            date: 'date' in item ? (item.date as string) : null,
        };
    });

    const datesAsDates = useMemo(() =>
        invoice.dates?.map(d => new Date(d.date)) || [],
    [invoice.dates]);

    const calculatedTotal = useInvoiceTotal(
        enforceNonNull(invoice.type),
        enforceNonNull(invoice.user_items),
        enforceNonNull(invoice.dates).map(d => new Date(d.date))
    );

    return (
        <div className="flex flex-column gap-2">
            {header} {/* Platzhalter für individuellen Header */}

            {isKG && (
                <>
                    <InvoiceCalendar dates={datesAsDates} onChange={() => {}}/>
                </>
            )}

            <Header title="Leistungsübersicht"/>
            <InvoiceItemTable invoiceItems={standardizedItems} type={enforceNonNull(invoice.type)} isLoading={false} />
            <Total total={calculatedTotal}/>

            <Header title="Details"/>
            <InvoiceDetails invoice={invoice} />

            <Header title="Patientendaten"/>
            <InvoicePatientData patient={selectedPatient}/>

            {footer} {/* Platzhalter für individuellen Footer */}
        </div>
    );
};
