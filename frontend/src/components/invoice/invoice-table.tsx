import React from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import { Tag } from "primereact/tag";
import {type Invoice, type Patient} from "../../api";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../../config/routes.ts";

interface InvoiceTableProps {
    invoices: Invoice[] | undefined;
    isLoading: boolean;
}

export const InvoiceTable: React.FC<InvoiceTableProps> = ({ invoices, isLoading }) => {
    const navigate = useNavigate();

    return (
        <DataTable
            value={invoices}
            paginator
            rows={10}
            key="invoice_id"
            tableStyle={{ minWidth: "50rem" }}
            emptyMessage="Keine Rechnungen gefunden"
            className="mt-2"
            stripedRows
            removableSort
            showGridlines
            loading={isLoading}
        >
            <Column field="invoice_number" header="Rechnungsnummer" className="font-bold" sortable />
            <Column field="invoice_date" header="Rechnungsdatum" sortable />
            <Column field="type" header="Rechnungstyp" sortable />
            <Column field="created_at" header="Erstellungsdatum" sortable
                    body={(e: Patient) => new Date(e.created_at).toLocaleString('de-DE', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    })}
            />
            <Column
                field="is_draft"
                header="Status"
                sortable
                body={(e: Invoice) => (
                    <Tag
                        severity={e.is_draft ? "warning" : "success"}
                        value={e.is_draft ? "Entwurf" : "Fertig"}
                        rounded
                    />
                )}
            />
            <Column
                header="Aktionen"
                alignHeader="right"
                body={(e: Invoice) => (
                    <div className="flex gap-2 justify-content-end">
                        <Button onClick={() => navigate(generatePath(ROUTES.INVOICE_CREATE, { id: e.invoice_id.toString() }))} icon="pi pi-pencil" className="p-button-rounded" />
                        <Button onClick={() => navigate(generatePath(ROUTES.INVOICE, { id: e.invoice_id.toString() }))} icon="pi pi-info-circle" className="p-button-rounded" />
                        <Button onClick={() => navigate(generatePath(ROUTES.INVOICE_PREVIEW, { id: e.invoice_id.toString() }))} icon="pi pi-file-pdf" className="p-button-rounded" />
                    </div>
                )}
            />
        </DataTable>
    );
};