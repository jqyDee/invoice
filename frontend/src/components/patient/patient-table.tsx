import React from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from "primereact/button";
import type { Patient } from "../../api";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../../config/routes.ts";
import { useIsMobile } from "../../hooks/use-is-mobile.ts";

interface PatientTableProps {
    patients: Patient[] | undefined;
    isPreview?: boolean;
    isLoading: boolean;
    onEdit: (patient: Patient) => void;
}

export const PatientTable: React.FC<PatientTableProps> = ({ patients, isPreview = false, isLoading, onEdit }) => {
    const navigate = useNavigate();
    const isMobile = useIsMobile();

    return (
        <DataTable
            value={patients}
            paginator
            rows={10}
            key="patient_id"
            emptyMessage="Keine Patienten gefunden."
            className="mt-2"
            breakpoint="960px"
            stripedRows
            showGridlines
            removableSort
            size="small"
            loading={isLoading}
        >
            {!isMobile && <Column field="label" header="Kürzel" />}
            <Column field="first_name" header="Vorname" sortable />
            <Column field="last_name" header="Nachname" sortable />
            {!isMobile && <Column field="city" header="Ort" />}
            {!isMobile && (
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
            )}
            {!isPreview &&
                <Column
                    alignHeader="right"
                    className="white-space-nowrap"
                    body={(e: Patient) => (
                        <div className="flex flex-column md:flex-row gap-2 justify-content-end align-items-end">
                            <div className="flex gap-2">
                                <Button
                                    icon="pi pi-file-pdf"
                                    className="p-button-rounded"
                                    tooltip="Therapie-Vereinbarung"
                                    tooltipOptions={{ showDelay: 1000 }}
                                    onClick={() => navigate(generatePath(ROUTES.THERAPY_PREVIEW, { id: e.patient_id.toString() }))}
                                />
                                <Button
                                    icon="pi pi-shield"
                                    className="p-button-rounded"
                                    tooltip="Datenschutzerklärung"
                                    tooltipOptions={{ showDelay: 1000 }}
                                    onClick={() => navigate(generatePath(ROUTES.PRIVACY_PREVIEW, { id: e.patient_id.toString() }))}
                                />
                            </div>
                            <div className="flex gap-2">
                                <Button
                                    onClick={() => onEdit(e)}
                                    icon="pi pi-pencil"
                                    tooltip="Bearbeiten"
                                    tooltipOptions={{ showDelay: 1000 }}
                                    className="p-button-rounded"
                                />
                            </div>
                        </div>
                    )}
                    header="Aktionen"
                />
            }
        </DataTable>
    );
};