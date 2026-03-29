import React from 'react';
import {useQuery} from "@tanstack/react-query";
import {getPatientsPatientsGetOptions} from "../api/@tanstack/react-query.gen.ts";
import {Button} from "primereact/button";
import type {Patient} from "../api";
import {Dialog} from "primereact/dialog";
import {PatientForm} from "./patient/patient-form.tsx";
import {InputText} from "primereact/inputtext";
import {PatientTable} from "./patient/patient-table.tsx";
import {Header} from "../utilities/header.tsx"; // Import Table
import {IconField} from 'primereact/iconfield';
import {InputIcon} from "primereact/inputicon";

export const PatientListView: React.FC = () => {
    const [visible, setVisible] = React.useState(false);
    const [selectedPatient, setSelectedPatient] = React.useState<Patient | null>(null);
    const [search, setSearch] = React.useState("");
    const [debouncedSearch, setDebouncedSearch] = React.useState("");

    React.useEffect(() => {
        const handler = setTimeout(() => setDebouncedSearch(search), 300);
        return () => clearTimeout(handler);
    }, [search]);

    const {data: patients, isLoading, isError} = useQuery({
        ...getPatientsPatientsGetOptions({
            query: {search: debouncedSearch || undefined}
        }),
    });

    const openEdit = (patient: Patient) => {
        setSelectedPatient(patient);
        setVisible(true);
    };

    if (isError) return <div className="text-red-500 p-5">Fehler beim Laden der Patienten.</div>;

    return (
        <div className="flex-column">
            <div className="flex flex-column md:flex-row md:justify-content-between md:align-items-center mb-3 gap-3">
                <Header title="Patienten"/>

                <div className="flex gap-2 w-full md:w-auto">
                    <IconField iconPosition="left" className="w-full">
                        <InputIcon className="pi pi-search"/>
                        <InputText
                            value={search}
                            placeholder="Suche..."
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full md:w-15rem"
                        />
                    </IconField>
                    <Button
                        onClick={() => {
                            setSelectedPatient(null);
                            setVisible(true);
                        }}
                        icon="pi pi-plus"
                        label="Neu"
                        className="p-button-rounded flex-shrink-0"
                    />
                </div>
            </div>

            <Dialog
                header={selectedPatient ? "Patient bearbeiten" : "Neuen Patienten anlegen"}
                visible={visible}
                style={{maxWidth: '80vw'}}
                onHide={() => setVisible(false)}
            >
                <PatientForm patientToEdit={selectedPatient} onSuccess={() => setVisible(false)}/>
            </Dialog>

            <PatientTable patients={patients} isLoading={isLoading} onEdit={openEdit}/>
        </div>
    );
};