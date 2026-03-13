import type {Patient} from "../../api";
import React from "react";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";

interface InvoicePatientDataProp {
    patient: Patient | undefined;
}

export const InvoicePatientData: React.FC<InvoicePatientDataProp> = ({patient}) => {
    const rows = [
        {label: "Kürzel", value: patient?.label || '-'},
        {label: "Name", value: `${patient?.first_name ?? '-'} ${patient?.last_name || '-'}`},
        {label: "Geschlecht", value: patient?.gender || '-'},
        {label: "Geburtsdatum", value: patient?.birthday || '-'},
        {
            label: "Adresse",
            value: `${patient?.street || '-'} ${patient?.street_number || '-'}, ${patient?.postal_code || '-'} ${patient?.city || '-'}`
        },
        {label: "Kontakt", value: `${patient?.email || '-'} / ${patient?.telephone || '-'}`}
    ];

    return (
        <DataTable value={rows} showGridlines className="p-datatable-sm p-datatable-striped">
            <Column field="label" style={{width: '30%', fontWeight: 'bold'}}/>
            <Column field="value"/>
        </DataTable>
    );
};