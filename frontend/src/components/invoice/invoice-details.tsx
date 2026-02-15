import React from "react";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import {InvoiceType} from "../../api";

interface InvoiceDetailsProp {
    type: InvoiceType;
    isDraft?: boolean;
    invoiceDate: string;
    invoiceNumber?: string;
    diagnosis: string;
}

export const InvoiceDetails: React.FC<InvoiceDetailsProp> = ({ type, isDraft, invoiceDate, invoiceNumber, diagnosis }) => {
    const rows = [
        {label: "Rechnungsdatum", value: invoiceDate},
        {label: "Rechnungsnummer", value: invoiceNumber ?? '-'},
        {label: "Entwurf", value: isDraft ?? 'false'}
    ]

    if (type === InvoiceType.HP) rows.push({label: "Diagnose", value: diagnosis})

    return (
        <DataTable value={rows} showGridlines className="p-datatable-sm p-datatable-striped">
            <Column field="label" style={{ width: '30%', fontWeight: 'bold' }}/>
            <Column field="value"/>
        </DataTable>
    )
}