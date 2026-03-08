import React from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { type Invoice, type InvoiceCreate, InvoiceType, type InvoiceUpdate } from "../../api";
import {toGermanStatus} from "../../utilities/status.ts";
import {toGermanDateString} from "../../utilities/local-date-string.ts";

interface InvoiceDetailsProp {
    invoice: Invoice | InvoiceCreate | InvoiceUpdate;
}

export const InvoiceDetails: React.FC<InvoiceDetailsProp> = ({ invoice }) => {
    const isFullInvoice = (inv: any): inv is Invoice => {
        return 'status' in inv && 'total_travel_distance' in inv;
    };

    const rows = [
        {
            label: "Rechnungsdatum",
            value: invoice.invoice_date ? toGermanDateString(new Date(invoice.invoice_date)) : '-' },
        {
            label: "Rechnungsnummer",
            value: ('invoice_number' in invoice) ? (invoice.invoice_number ?? '-') : '-'
        },
        {
            label: "Status",
            value: toGermanStatus(('status' in invoice) ? invoice.status : 'DRAFT')
        },
    ];

    // Add payment info if it's a full invoice
    if (isFullInvoice(invoice)) {
        rows.push({
            label: "Bezahlt am",
            value: invoice.paid_at ? toGermanDateString(new Date(invoice.paid_at)) :  '-'
        });
        rows.push({
            label: "Kilometer pro Fahrt",
            value: `${invoice.kilometers_at_billing?.toFixed(1) ?? '-'} km`
        });
        rows.push({
            label: "Gesamt Kilometer",
            value: `${invoice.total_travel_distance.toFixed(1)} km`
        });
    }

    // Add diagnosis for HP invoices
    if (invoice.type === InvoiceType.HP) {
        rows.push({ label: "Diagnose", value: invoice.diagnosis ?? '-' });
    }

    return (
        <DataTable value={rows} showGridlines className="p-datatable-sm p-datatable-striped">
            <Column field="label" style={{ width: '30%', fontWeight: 'bold' }} />
            <Column field="value" />
        </DataTable>
    );
};