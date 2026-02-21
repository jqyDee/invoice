import React, {useState} from 'react';
import {AutoComplete, type AutoCompleteCompleteEvent} from 'primereact/autocomplete';
import {Button} from 'primereact/button';
import {useQuery} from '@tanstack/react-query';
import {getPatientsPatientsGetOptions} from "../../api/@tanstack/react-query.gen.ts";
import {type Invoice, type InvoiceCreate, InvoiceType, type InvoiceUpdate, type Patient} from "../../api";
import {SelectButton} from "primereact/selectbutton";
import {Header} from "../../utilities/header.tsx";
import {InvoicePatientData} from "../invoice/invoice-patient-data.tsx";

interface StepContentProps {
    invoice: Invoice | InvoiceCreate | InvoiceUpdate;
    onChange: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    next: () => void;
}

export const StepGeneralContent: React.FC<StepContentProps> = ({ invoice, onChange, next }) => {
    const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);

    const { data: patients } = useQuery(getPatientsPatientsGetOptions());
    const selectedPatient = patients?.find(p => p.patient_id === invoice.patient_id);

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
                    onChange={(e) => onChange({ patient_id: e.value.patient_id })}
                    placeholder="Name oder Kürzel suchen..."
                    className="w-full"
                    forceSelection
                />
            </div>
            <div className="col-6 flex flex-column">
                <Header title="Rechnungstyp" />
                <SelectButton
                    value={invoice.type}
                    options={Object.values(InvoiceType)}
                    onChange={e => onChange({ type: e.value })}
                />
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
                    disabled={!selectedPatient || !invoice.type}
                    onClick={next}
                />
            </div>
        </div>
    );
};