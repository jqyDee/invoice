import React, {useMemo, useState} from 'react';
import {Dialog} from 'primereact/dialog';
import {DataTable, type DataTableExpandedRows} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {InputText} from 'primereact/inputtext';
import {useQuery} from '@tanstack/react-query';
import {
    getInvoicesInvoicesGetOptions,
} from '../../api/@tanstack/react-query.gen.ts';
import {
    getInvoiceTemplateEndpointInvoicesInvoiceIdTemplateGet,
    type Invoice,
    type InvoiceDateGroup,
    type InvoiceItemCreate,
    InvoiceType,
} from '../../api';
import {toGermanDateString} from '../../utilities/local-date-string.ts';

interface InvoiceTemplateInvoicePickerProps {
    visible: boolean;
    onHide: () => void;
    invoiceType: InvoiceType;
    patientId: number;
    onSelect: (user_items: InvoiceItemCreate[], date_groups?: InvoiceDateGroup[]) => void;
}

export const InvoiceTemplateInvoicePicker: React.FC<InvoiceTemplateInvoicePickerProps> = ({
                                                                                              visible,
                                                                                              onHide,
                                                                                              invoiceType,
                                                                                              patientId,
                                                                                              onSelect,
                                                                                          }) => {
    const isKGorGT = invoiceType === InvoiceType.KG || invoiceType === InvoiceType.GT;

    const [filter, setFilter] = useState('');
    const [expandedRows, setExpandedRows] = useState<DataTableExpandedRows>({});

    const {data: allInvoices = []} = useQuery(getInvoicesInvoicesGetOptions({
        query: {
            invoice_type: invoiceType,
            show_drafts: false
        }
    }));

    const filteredInvoices = useMemo(() => {
        const lower = filter.toLowerCase();
        const typed = allInvoices.filter(inv => inv.type === invoiceType);
        const filtered = filter
            ? typed.filter(inv =>
                (inv.invoice_number ?? '').toLowerCase().includes(lower) ||
                `${inv.patient.first_name} ${inv.patient.last_name}`.toLowerCase().includes(lower) ||
                inv.user_items.some(i => i.description.toLowerCase().includes(lower))
            )
            : typed;

        return [...filtered].sort((a, b) => {
            const aCurrent = a.patient_id === patientId ? 0 : 1;
            const bCurrent = b.patient_id === patientId ? 0 : 1;
            return aCurrent - bCurrent || new Date(b.invoice_date).getTime() - new Date(a.invoice_date).getTime();
        });
    }, [allInvoices, patientId, filter, invoiceType]);

    const handleHide = () => {
        setFilter('');
        setExpandedRows({});
        onHide();
    };

    const rowExpansionTemplate = (inv: Invoice) => {
        if (isKGorGT) {
            return (
                <DataTable value={inv.user_items} size="small" className="p-2">
                    <Column field="description" header="Beschreibung" style={{width: '70%'}}/>
                    <Column header="Betrag" body={(i) => `${i.amount.toFixed(2)} €`} style={{width: '15%'}}/>
                    <Column header="Anzahl" field="quantity" style={{width: '15%'}}/>
                </DataTable>
            );
        } else {
            return (
                <div className="p-2 flex flex-column gap-2">
                    {inv.dates.map(d => (
                        <div key={d.date_id ?? d.date}>
                            <div
                                className="font-semibold mb-1">{toGermanDateString(new Date(d.date + 'T00:00:00'))}</div>
                            <DataTable value={d.items ?? []} size="small">
                                <Column field="number" header="Ziffer" style={{width: '15%'}}/>
                                <Column field="description" header="Beschreibung" style={{width: '60%'}}/>
                                <Column header="Betrag" body={(i) => `${i.amount.toFixed(2)} €`}
                                        style={{width: '15%'}}/>
                                <Column header="Anzahl" field="quantity" style={{width: '10%'}}/>
                            </DataTable>
                        </div>
                    ))}
                </div>
            );
        }
    };

    const handleSelectInvoice = async (invoice: Invoice) => {
        const {data: template} = await getInvoiceTemplateEndpointInvoicesInvoiceIdTemplateGet({
            path: {invoice_id: invoice.invoice_id},
            throwOnError: true,
        })

        if (isKGorGT) {
            onSelect(template?.user_items ?? []);
        } else {
            onSelect([], template?.date_groups);
        }
        handleHide();
    };

    const patientTemplate = (inv: Invoice) =>
        `${inv.patient.first_name} ${inv.patient.last_name}`;

    const dateTemplate = (inv: Invoice) =>
        toGermanDateString(new Date(inv.invoice_date + 'T00:00:00'));

    const rowClassName = (inv: Invoice) =>
        inv.patient_id === patientId ? 'font-bold' : '';

    return (
        <Dialog
            header="Vorlage laden"
            visible={visible}
            onHide={handleHide}
            style={{width: '60vw', maxWidth: '900px'}}
        >
            <div className="flex flex-column gap-3">
                <InputText
                    placeholder="Nach Rechnungsnummer oder Patient filtern..."
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                    className="w-full"
                />
                <DataTable
                    value={filteredInvoices}
                    dataKey="invoice_id"
                    selectionMode="single"
                    onRowSelect={e => handleSelectInvoice(e.data as Invoice)}
                    emptyMessage="Keine Rechnungen gefunden."
                    stripedRows
                    size="small"
                    rowClassName={rowClassName}
                    style={{cursor: 'pointer'}}
                    expandedRows={expandedRows}
                    onRowToggle={(e) => setExpandedRows(e.data as DataTableExpandedRows)}
                    rowExpansionTemplate={rowExpansionTemplate}
                    paginator
                    rows={20}
                    rowsPerPageOptions={[10, 20, 50]}
                >
                    <Column expander style={{width: '3rem'}}/>
                    <Column field="invoice_number" header="Rechnungsnr." style={{width: '20%'}}/>
                    <Column header="Patient" body={patientTemplate} style={{width: '40%'}}/>
                    <Column header="Datum" body={dateTemplate} style={{width: '20%'}}/>
                    <Column
                        header="Positionen"
                        body={(inv: Invoice) => {
                            return isKGorGT
                                ? inv.user_items.length
                                : inv.dates.reduce((s, d) => s + (d.items?.length ?? 0), 0);
                        }}
                        style={{width: '20%'}}
                    />
                </DataTable>
            </div>
        </Dialog>
    );
};
