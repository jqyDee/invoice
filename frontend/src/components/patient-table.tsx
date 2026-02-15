import React from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from "primereact/button";
import type { Patient } from "../api";

interface PatientTableProps {
    patients: Patient[] | undefined;
    isPreview?: boolean;
    isLoading: boolean;
    onEdit: (patient: Patient) => void;
}

export const PatientTable: React.FC<PatientTableProps> = ({ patients, isPreview = false, isLoading, onEdit }) => {
    return (
        <DataTable
            value={patients}
            paginator
            rows={10}
            key="patient_id"
            tableStyle={{ minWidth: '50rem' }}
            emptyMessage="Keine Patienten gefunden."
            className="mt-2"
            stripedRows
            showGridlines
            removableSort
            loading={isLoading}
        >
            <Column field="label" header="Kürzel" className="font-bold" />
            <Column field="first_name" header="Vorname" sortable />
            <Column field="last_name" header="Nachname" sortable />
            <Column field="city" header="Ort" />
            <Column
                field="created_at"
                header="Erstellungsdatum"
                sortable
                body={(e: Patient) => new Date(e.created_at).toLocaleString('de-DE', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                })}
            />
            {!isPreview &&
                <Column
                    body={(e: Patient) => (
                        <Button onClick={() => onEdit(e)} icon="pi pi-pencil" label="Bearbeiten" className="p-button-rounded" />
                    )}
                    header="Aktionen"
                />
            }
        </DataTable>
    );
};