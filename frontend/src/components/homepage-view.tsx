import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPatientsPatientsGetOptions, getInvoicesInvoicesGetOptions } from "../api/@tanstack/react-query.gen.ts";
import { PatientTable } from './patient/patient-table.tsx';
import { InvoiceTable } from './invoice/invoice-table.tsx';
import {Header} from "../utilities/header.tsx";

export const HomepageView: React.FC = () => {
    const { data: patients, isLoading: patientsLoading } = useQuery(getPatientsPatientsGetOptions());

    const { data: drafts, isLoading: draftsLoading } = useQuery({
        ...getInvoicesInvoicesGetOptions({
            query: { only_drafts: true } // Show only drafts
        })
    });

    return (
        <div className="flex flex-column gap-4">
            <section>
                <Header title="Aktuelle Entwürfe"/>
                <InvoiceTable invoices={drafts} isLoading={draftsLoading} />
            </section>

            <section>
                <Header title="Patientenübersicht"/>
                <PatientTable patients={patients} isPreview={true} isLoading={patientsLoading} onEdit={() => {}} />
            </section>
        </div>
    );
};