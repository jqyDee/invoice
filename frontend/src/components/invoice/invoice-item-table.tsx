import {type InvoiceItem, type InvoiceItemCreate, InvoiceType} from "../../api";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import React from "react";


interface InvoiceItemTableProps {
    invoiceItems: InvoiceItem[] | InvoiceItemCreate[];
    type: InvoiceType;
    isLoading: boolean;
}

export const InvoiceItemTable: React.FC<InvoiceItemTableProps> = ({ invoiceItems, type, isLoading }) => {
    const isKG = (type === InvoiceType.KG);

    return (
        <DataTable
            value={invoiceItems}
            key="description"
            showGridlines
            tableStyle={{ minWidth: '50rem' }}
            emptyMessage="Keine Behandlungsarten gefunden."
            className="w-full p-datatable-striped"
            loading={isLoading}
        >
            {!isKG && <Column field="date" header="Datum"/>}
            {!isKG && <Column field="number" header="Ziffer"/>}
            {isKG && <Column field="quantity" header="Anzahl"/>}
            <Column field="description" header="Beschreibung"/>
            <Column field="amount"
                    header="Einzelbetrag"
                    align="right"
                    body={(e: InvoiceItem | InvoiceItemCreate) =>
                        <span>{e.amount.toFixed(2)} €</span>
                    }/>
        </DataTable>
    )
}