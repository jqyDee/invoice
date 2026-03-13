import React, {useState} from 'react';
import {Button} from 'primereact/button';
import {
    InvoiceType,
    type InvoiceCreate,
    type InvoiceUpdate,
    type InvoiceItemCreate,
    type InvoiceDateGroup
} from "../../api";
import {InvoiceCalendar} from "../invoice/invoice-calendar.tsx";
import {Header} from "../../utilities/header.tsx";
import {Total} from "../../utilities/total.tsx";
import {useInvoiceTotal} from "../../hooks/invoice/use-invoice-total.ts";
import {enforceNonNull} from "../../utilities/enforce-non-null.ts";
import {toLocalDateString} from "../../utilities/local-date-string.ts";
import {InvoiceItemTable} from "../invoice/invoice-item-table.tsx";
import {InvoiceDefaultItemTable} from "../invoice/invoice-default-item-table.tsx";
import {useQuery} from "@tanstack/react-query";
import {
    getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions,
    getInvoicesInvoicesGetOptions
} from "../../api/@tanstack/react-query.gen.ts";
import {InvoiceTemplateInvoicePicker} from "../invoice/invoice-template-invoice-picker.tsx";
import {getLastKGInvoiceItems} from "../../utilities/template-items.ts";

interface StepItemsProps {
    invoice: InvoiceCreate | InvoiceUpdate
    onChange: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    prev: () => void;
    next: () => void;
}

export const StepItemsContent: React.FC<StepItemsProps> = ({invoice, onChange, prev, next}) => {
    const isKGorGT = invoice.type === InvoiceType.KG || invoice.type === InvoiceType.GT;
    const [templatePickerVisible, setTemplatePickerVisible] = useState(false);

    const {data: allInvoices = []} = useQuery(getInvoicesInvoicesGetOptions({
        query: {
            invoice_type: invoice.type,
            show_drafts: false
        }
    }));

    const handleLoadLastKG = () => {
        const items = getLastKGInvoiceItems(allInvoices, invoice.patient_id!, invoice.type!);
        if (items) onChange({user_items: items});
    };

    const handleTemplateSelect = (user_items: InvoiceItemCreate[], date_groups?: InvoiceDateGroup[]) => {
        if (isKGorGT) {
            onChange({user_items});
        } else if (date_groups && date_groups.length > 0) {
            const existingDates = invoice.dates || [];
            if (existingDates.length > 0) {
                // Positional replacement: keep existing dates, replace items
                onChange({
                    dates: existingDates.map((d, i) => ({
                        ...d,
                        items: date_groups[i]?.items ?? d.items,
                    })),
                });
            } else {
                // No existing dates: create new date entries from the template
                onChange({
                    dates: date_groups.map(g => ({
                        date: g.date,
                        items: g.items,
                    })),
                });
            }
        }
    };

    const {data: availableDefaults} = useQuery(
        getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({query: {invoice_type: invoice.type}})
    );
    const selectedDefaults = (availableDefaults || [])
        .filter(d => invoice.default_item_ids?.includes(d.default_item_id));

    const userItems = isKGorGT
        ? (invoice.user_items || [])
        : (invoice.dates || []).flatMap(d => d.items || []);

    const calculatedTotal = useInvoiceTotal(
        [...userItems, ...selectedDefaults],
        enforceNonNull(invoice.dates).map(d => new Date(d.date)),
        enforceNonNull(invoice.type)
    );

    // Calculate item count to disable the Next button safely
    const itemCount = isKGorGT
        ? (invoice.user_items?.length || 0)
        : (invoice.dates?.flatMap(d => d.items || []).length || 0);

    return (
        <div className="flex flex-column gap-4">
            {/* Standalone Calendar for KG Dates */}
            {isKGorGT && (
                <InvoiceCalendar
                    dates={invoice.dates?.map(d => new Date(d.date)) || []}
                    onChange={(e) =>
                        onChange({dates: (e.value as Date[]).map(d => ({date: toLocalDateString(d)}))})
                    }
                />
            )}

            <div className="flex flex-column md:flex-row justify-content-between md:align-items-center gap-3">
                <Header title="Leistungen"/>
                <div className="flex gap-2">
                    <Button
                        label="Vorlage laden"
                        icon="pi pi-copy"
                        className="p-button-outlined p-button-contrast"
                        onClick={() => setTemplatePickerVisible(true)}
                    />
                    {isKGorGT && (
                        <Button
                            label="Letzte Vorlage"
                            icon="pi pi-history"
                            className="p-button-outlined p-button-contrast"
                            onClick={handleLoadLastKG}
                        />
                    )}
                </div>
            </div>
            <InvoiceTemplateInvoicePicker
                visible={templatePickerVisible}
                onHide={() => setTemplatePickerVisible(false)}
                invoiceType={invoice.type!}
                patientId={invoice.patient_id!}
                onSelect={handleTemplateSelect}
            />
            <InvoiceItemTable invoice={invoice} onChange={onChange} readonly={false} patientId={invoice.patient_id!}/>

            <InvoiceDefaultItemTable invoice={invoice} onChange={onChange}/>
            <Total total={calculatedTotal}/>

            {/* Footer Navigation */}
            <div className="flex justify-content-between">
                <Button label="Zurück" icon="pi pi-arrow-left" className="p-button-text" onClick={prev}/>
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={
                        (itemCount === 0 && (!invoice.default_item_ids || invoice.default_item_ids.length === 0)) ||
                        (isKGorGT && (!invoice.dates || invoice.dates.length === 0))
                    }
                    onClick={next}
                />
            </div>
        </div>
    );
};