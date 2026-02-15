import React from 'react';
import { useQuery } from "@tanstack/react-query";
import { getPatientsPatientsGetOptions } from "../api/@tanstack/react-query.gen.ts";
import { Button } from "primereact/button";
import type { Patient } from "../api";
import { Dialog } from "primereact/dialog";
import { PatientForm } from "./patient-form.tsx";
import { InputText } from "primereact/inputtext";
import { PatientTable } from "./patient-table";
import {Header} from "./header.tsx"; // Import Table

export const PatientList: React.FC = () => {
    const [visible, setVisible] = React.useState(false);
    const [selectedPatient, setSelectedPatient] = React.useState<Patient | null>(null);
    const [search, setSearch] = React.useState("");
    const [debouncedSearch, setDebouncedSearch] = React.useState("");

    React.useEffect(() => {
        const handler = setTimeout(() => setDebouncedSearch(search), 300);
        return () => clearTimeout(handler);
    }, [search]);

    const { data: patients, isLoading, isError, refetch } = useQuery({
        ...getPatientsPatientsGetOptions({
            query: { search: debouncedSearch || undefined }
        }),
    });

    const openEdit = (patient: Patient) => {
        setSelectedPatient(patient);
        setVisible(true);
    };

    if (isError) return <div className="text-red-500 p-5">Fehler beim Laden der Patienten.</div>;

    return (
        <div className="flex-column">
            <div className="flex justify-content-between">
                <Header title="Patienten"/>
                <div className="flex align-items-center gap-2">
                    <Button onClick={() => { setSelectedPatient(null); setVisible(true); }} icon="pi pi-plus" label="Neuer Patient" className="p-button-rounded" />
                    <InputText value={search} placeholder="Suche..." onChange={(e) => setSearch(e.target.value)} style={{ minWidth: "20vw" }} />
                </div>
            </div>

            <Dialog
                header={selectedPatient ? "Patient bearbeiten" : "Neuen Patienten anlegen"}
                visible={visible}
                style={{ maxWidth: '50vw' }}
                onHide={() => setVisible(false)}
            >
                <PatientForm patientToEdit={selectedPatient} onSuccess={() => setVisible(false)} refetch={refetch} />
            </Dialog>

            <PatientTable patients={patients} isLoading={isLoading} onEdit={openEdit} />
        </div>
    );
};