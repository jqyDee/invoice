import React from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from "primereact/button";
import type { Patient } from "../../api";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../../config/routes.ts";

interface PatientTableProps {
    patients: Patient[] | undefined;
    isPreview?: boolean;
    isLoading: boolean;
    onEdit: (patient: Patient) => void;
}

export const PatientTable: React.FC<PatientTableProps> = ({ patients, isPreview = false, isLoading, onEdit }) => {
    const navigate = useNavigate();

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
                    alignHeader="right"
                    body={(e: Patient) => (
                        <div className="flex justify-content-end gap-2">
                            <Button
                                icon="pi pi-file-pdf"
                                className="p-button-rounded"
                                onClick={() => navigate(generatePath(ROUTES.THERAPY_PREVIEW, { id: e.patient_id.toString() }))}
                            />
                            <Button
                                onClick={() => onEdit(e)}
                                icon="pi pi-pencil"
                                tooltip="Bearbeiten"
                                tooltipOptions={{ showDelay: 1000 }}
                                className="p-button-rounded"
                            />
                        </div>
                    )}
                    header="Aktionen"
                />
            }
        </DataTable>
    );
};