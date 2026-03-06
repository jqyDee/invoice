import React from 'react';
import { Button } from 'primereact/button';
import { InvoiceType, type InvoiceCreate, type InvoiceUpdate } from "../../api";
import { InvoiceCalendar } from "../invoice/invoice-calendar.tsx";
import { Header } from "../../utilities/header.tsx";
import { Total } from "../../utilities/total.tsx";
import { useInvoiceTotal } from "../../hooks/invoice/use-invoice-total.ts";
import { enforceNonNull } from "../../utilities/enforce-non-null.ts";
import { toLocalDateString } from "../../utilities/local-date-string.ts";
import {InvoiceItemTable} from "../invoice/invoice-item-table.tsx";
import {InvoiceDefaultItemTable} from "../invoice/invoice-default-item-table.tsx";

interface StepItemsProps {
    invoice: InvoiceCreate | InvoiceUpdate
    onChange: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    prev: () => void;
    next: () => void;
}

export const StepItemsContent: React.FC<StepItemsProps> = ({ invoice, onChange, prev, next }) => {
    const isKG = invoice.type === InvoiceType.KG;

    const calculatedTotal = useInvoiceTotal(
        enforceNonNull(invoice.type),
        enforceNonNull(invoice.user_items),
        enforceNonNull(invoice.dates).map(d => new Date(d.date))
    );

    // Calculate item count to disable the Next button safely
    const itemCount = isKG
        ? (invoice.user_items?.length || 0)
        : (invoice.dates?.flatMap(d => d.items || []).length || 0);

    return (
        <div className="flex flex-column gap-4">
            {/* Standalone Calendar for KG Dates */}
            {isKG && (
                <InvoiceCalendar
                    dates={invoice.dates?.map(d => new Date(d.date)) || []}
                    onChange={(e) =>
                        onChange({ dates: (e.value as Date[]).map(d => ({ date: toLocalDateString(d) })) })
                    }
                />
            )}

            <Header title="Leistungen" />
            <InvoiceItemTable invoice={invoice} onChange={onChange} readonly={false}/>

            <InvoiceDefaultItemTable invoice={invoice} onChange={onChange}/>
            <Total total={calculatedTotal}/>

            {/* Footer Navigation */}
            <div className="flex justify-content-between">
                <Button label="Zurück" icon="pi pi-arrow-left" className="p-button-text" onClick={prev} />
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={
                        (itemCount === 0 && (!invoice.default_item_ids || invoice.default_item_ids.length === 0)) ||
                        (isKG && (!invoice.dates || invoice.dates.length === 0))
                    }
                    onClick={next}
                />
            </div>
        </div>
    );
};