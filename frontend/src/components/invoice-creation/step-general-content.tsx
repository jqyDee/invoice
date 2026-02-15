import React, {useState} from 'react';
import {AutoComplete, type AutoCompleteCompleteEvent} from 'primereact/autocomplete';
import {Button} from 'primereact/button';
import {useQuery} from '@tanstack/react-query';
import {getPatientsPatientsGetOptions} from "../../api/@tanstack/react-query.gen.ts";
import {InvoiceType, type Patient} from "../../api";
import {SelectButton, type SelectButtonChangeEvent} from "primereact/selectbutton";
import {Header} from "../header.tsx";
import {InvoicePatientData} from "../invoice/invoice-patient-data.tsx";

interface StepContentProps {
    next: (patient: Patient, invoiceType: InvoiceType) => void;
    initialPatient?: Patient | null;
    initialType?: InvoiceType | null;
}

export const StepGeneralContent: React.FC<StepContentProps> = ({ next, initialPatient, initialType }) => {
    const [selectedPatient, setSelectedPatient] = useState<Patient | undefined>(initialPatient || undefined);
    const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
    const [invoiceType, setInvoiceType] = useState<InvoiceType | undefined>(initialType || undefined);

    const { data: patients } = useQuery(getPatientsPatientsGetOptions());

    const searchPatients = (event: AutoCompleteCompleteEvent) => {
        const query = event.query.toLowerCase();
        const _filtered = (patients || []).filter((p) => {
            return (
                p.first_name.toLowerCase().includes(query) ||
                p.last_name.toLowerCase().includes(query) ||
                p.label.toLowerCase().includes(query)
            );
        });
        setFilteredPatients(_filtered);
    };

    const itemTemplate = (item: Patient) => {
        return (
            <div className="flex align-items-center">
                <span className="font-bold mr-2">[{item.label}]</span>
                <span>{item.first_name} {item.last_name}</span>
            </div>
        );
    };

    return (
        <div className="grid">
            <div className="col-6 flex flex-column">
                <Header title="Patient auswählen"/>
                <AutoComplete
                    value={selectedPatient}
                    suggestions={filteredPatients}
                    completeMethod={searchPatients}
                    field="label"
                    dropdown
                    autoHighlight={true}
                    itemTemplate={itemTemplate}
                    onChange={(e) => setSelectedPatient(e.value)}
                    placeholder="Name oder Kürzel suchen..."
                    className="w-full"
                    forceSelection
                />
            </div>
            <div className="col-6 flex flex-column">
                <Header title="Rechnungstyp" />
                <SelectButton value={invoiceType} onChange={(e: SelectButtonChangeEvent) => setInvoiceType(e.value)} options={Object.values(InvoiceType)} />
            </div>
            <div className="col-12 flex flex-column">
                <Header title="Patientendaten"/>
                <InvoicePatientData patient={selectedPatient}/>
            </div>
            <div className="col-12 flex justify-content-end">
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={!selectedPatient || !invoiceType}
                    onClick={() => next(selectedPatient as Patient, invoiceType as InvoiceType)}
                />
            </div>
        </div>
    );
};