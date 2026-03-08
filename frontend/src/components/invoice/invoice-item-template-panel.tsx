import React, { useState, useMemo } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { useQuery } from '@tanstack/react-query';
import {
    getTemplateItemsEndpointInvoicesTemplateItemsGetOptions,
} from '../../api/@tanstack/react-query.gen.ts';
import { InvoiceType, type TemplateItemResponse } from '../../api';
import type { TreatmentFormData } from './invoice-treatment-form.tsx';

interface InvoiceItemTemplatePanelProps {
    patientId: number;
    invoiceType: InvoiceType;
    onSelect: (item: Partial<TreatmentFormData>) => void;
}

export const InvoiceItemTemplatePanel: React.FC<InvoiceItemTemplatePanelProps> = ({
    patientId, invoiceType, onSelect,
}) => {
    const isHP = invoiceType === InvoiceType.HP;
    const [expanded, setExpanded] = useState(false);
    const [filter, setFilter] = useState('');

    const { data: allItems = [] } = useQuery(
        getTemplateItemsEndpointInvoicesTemplateItemsGetOptions({ query: { invoice_type: invoiceType } })
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
            item.description.toLowerCase().includes(lower) ||
            (isHP && (item.number ?? '').toLowerCase().includes(lower))
        );
    }, [allItems, patientId, filter, isHP]);

    const handleRowSelect = (item: TemplateItemResponse) => {
        onSelect({
            description: item.description,
            amount: item.amount,
            number: item.number ?? undefined,
            quantity: item.quantity,
        });
        setExpanded(false);
        setFilter('');
    };

    const rowClassName = (item: TemplateItemResponse) =>
        item.patient_id === patientId ? 'font-bold' : '';

    const patientNameBody = (item: TemplateItemResponse) =>
        `${item.patient_first_name} ${item.patient_last_name}`;

    return (
        <div className="mb-3">
            <Button
                label={expanded ? 'Aus Vorlage wählen ▲' : 'Aus Vorlage wählen ▼'}
                className="p-button-text p-button-sm"
                onClick={() => setExpanded(v => !v)}
                type="button"
            />
            {expanded && (
                <div className="mt-2 border-1 surface-border border-round p-3 flex flex-column gap-2">
                    <InputText
                        placeholder="Nach Beschreibung filtern..."
                        value={filter}
                        onChange={e => setFilter(e.target.value)}
                        className="w-full"
                        size={undefined}
                    />
                    <DataTable
                        value={filtered}
                        selectionMode="single"
                        onRowSelect={e => handleRowSelect(e.data as TemplateItemResponse)}
                        emptyMessage="Keine Vorlagen gefunden."
                        stripedRows
                        size="small"
                        rowClassName={rowClassName}
                        style={{ cursor: 'pointer' }}
                        paginator
                        rows={10}
                        rowsPerPageOptions={[10, 25, 50]}
                    >
                        <Column field="description" header="Beschreibung" style={{ width: isHP ? '50%' : '65%' }} />
                        {isHP && <Column field="number" header="Ziffer" style={{ width: '15%' }} />}
                        <Column
                            field="amount"
                            header="Betrag"
                            body={(item: TemplateItemResponse) => `${item.amount.toFixed(2)} €`}
                            style={{ width: '15%' }}
                        />
                        <Column header="Patient" body={patientNameBody} style={{ width: '20%' }} />
                    </DataTable>
                </div>
            )}
        </div>
    );
};
