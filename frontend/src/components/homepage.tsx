import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPatientsPatientsGetOptions, getInvoicesInvoicesGetOptions } from "../api/@tanstack/react-query.gen.ts";
import { PatientTable } from './patient-table';
import { InvoiceTable } from './invoice-table';

export const Homepage: React.FC = () => {
    const { data: patients, isLoading: patientsLoading } = useQuery(getPatientsPatientsGetOptions());

    const { data: drafts, isLoading: draftsLoading } = useQuery({
        ...getInvoicesInvoicesGetOptions({
            query: { only_drafts: true } // Show only drafts
        })
    });

    return (
        <div className="flex flex-column gap-4">
            <section>
                <h2 className="text-3xl mb-2">Aktuelle Entwürfe</h2>
                <InvoiceTable invoices={drafts} isLoading={draftsLoading} />
            </section>

            <section>
                <h2 className="text-3xl mb-2">Patientenübersicht</h2>
                <PatientTable patients={patients} isPreview={true} isLoading={patientsLoading} onEdit={() => {}} />
            </section>
        </div>
    );
};