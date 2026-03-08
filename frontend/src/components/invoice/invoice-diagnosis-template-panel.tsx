import React, { useState, useMemo } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { useQuery } from '@tanstack/react-query';
import {
    getTemplateDiagnosesEndpointInvoicesTemplateDiagnosesGetOptions,
} from '../../api/@tanstack/react-query.gen.ts';
import { type DiagnosisTemplateResponse } from '../../api';

interface InvoiceDiagnosisTemplatePanelProps {
    patientId: number;
    onSelect: (diagnosis: string) => void;
}

export const InvoiceDiagnosisTemplatePanel: React.FC<InvoiceDiagnosisTemplatePanelProps> = ({
    patientId, onSelect,
}) => {
    const [expanded, setExpanded] = useState(false);
    const [filter, setFilter] = useState('');

    const { data: allItems = [] } = useQuery(
        getTemplateDiagnosesEndpointInvoicesTemplateDiagnosesGetOptions()
    );

    const filtered = useMemo(() => {
        const sorted = [...allItems].sort((a, b) => {
            const aCurrent = a.patient_id === patientId ? 0 : 1;
            const bCurrent = b.patient_id === patientId ? 0 : 1;
            return aCurrent - bCurrent;
        });
        if (!filter) return sorted;
        const lower = filter.toLowerCase();
        return sorted.filter(item =>
            item.diagnosis.toLowerCase().includes(lower)
        );
    }, [allItems, patientId, filter]);

    const handleRowSelect = (item: DiagnosisTemplateResponse) => {
        onSelect(item.diagnosis);
        setExpanded(false);
        setFilter('');
    };

    const rowClassName = (item: DiagnosisTemplateResponse) =>
        item.patient_id === patientId ? 'font-bold' : '';

    const patientNameBody = (item: DiagnosisTemplateResponse) =>
        `${item.patient_first_name} ${item.patient_last_name}`;

    return (
        <div className="mb-3">
            <Button
                label={expanded ? 'Aus Vorlage wählen ▲' : 'Aus Vorlage wählen ▼'}
                className="p-button-outlined p-button-contrast p-button-sm w-12 md:w-auto"
                onClick={() => setExpanded(v => !v)}
                type="button"
            />
            {expanded && (
                <div className="mt-2 border-1 border-round-sm p-3 flex flex-column gap-2">
                    <InputText
                        placeholder="Nach Diagnose filtern..."
                        value={filter}
                        onChange={e => setFilter(e.target.value)}
                        className="w-full"
                        size={undefined}
                    />
                    <DataTable
                        value={filtered}
                        selectionMode="single"
                        onRowSelect={e => handleRowSelect(e.data as DiagnosisTemplateResponse)}
                        emptyMessage="Keine Vorlagen gefunden."
                        stripedRows
                        size="small"
                        rowClassName={rowClassName}
                        style={{ cursor: 'pointer' }}
                        paginator
                        rows={10}
                        rowsPerPageOptions={[10, 25, 50]}
                    >
                        <Column field="diagnosis" header="Diagnose" style={{ width: '60%' }} />
                        <Column header="Patient" body={patientNameBody} style={{ width: '25%' }} />
                        <Column field="invoice_date" header="Datum" style={{ width: '15%' }} />
                    </DataTable>
                </div>
            )}
        </div>
    );
};
