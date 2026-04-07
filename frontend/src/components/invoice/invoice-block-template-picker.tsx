import React, {useState, useMemo} from 'react';
import {Dialog} from 'primereact/dialog';
import {DataTable, type DataTableExpandedRows} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {InputText} from 'primereact/inputtext';
import {useQuery} from '@tanstack/react-query';
import {getInvoicesInvoicesGetOptions} from '../../api/@tanstack/react-query.gen.ts';
import {InvoiceType, type InvoiceItemCreate} from '../../api';
import {toGermanDateString} from '../../utilities/local-date-string.ts';

interface BlockEntry {
    key: string;
    patientId: number;
    patientName: string;
    invoiceNumber: string | null;
    invoiceDate: string;
    blockDate: string;
    items: InvoiceItemCreate[];
}

interface InvoiceBlockTemplatePickerProps {
    visible: boolean;
    onHide: () => void;
    patientId: number;
    onSelect: (items: InvoiceItemCreate[]) => void;
}

export const InvoiceBlockTemplatePicker: React.FC<InvoiceBlockTemplatePickerProps> = ({
                                                                                          visible,
                                                                                          onHide,
                                                                                          patientId,
                                                                                          onSelect,
                                                                                      }) => {
    const [filter, setFilter] = useState('');
    const [expandedRows, setExpandedRows] = useState<DataTableExpandedRows>({});

    const {data: invoicesData} = useQuery(
        getInvoicesInvoicesGetOptions({query: {invoice_types: [InvoiceType.HP], show_drafts: false, size: 9999}})
    );
    const allInvoices = invoicesData?.items ?? [];

    const blocks = useMemo<BlockEntry[]>(() => {
        const result: BlockEntry[] = [];
        for (const invoice of allInvoices) {
            const patientName = `${invoice.patient.first_name} ${invoice.patient.last_name}`;
            for (const date of invoice.dates) {
                const items = (date.items ?? []).map(i => ({
                    description: i.description,
                    amount: i.amount,
                    number: i.number,
                    quantity: i.quantity,
                }));
                if (items.length === 0) continue;
                result.push({
                    key: `${invoice.invoice_number ?? invoice.invoice_id}_${date.date}`,
                    patientId: invoice.patient_id,
                    patientName,
                    invoiceNumber: invoice.invoice_number ?? null,
                    invoiceDate: invoice.invoice_date,
                    blockDate: date.date,
                    items,
                });
            }
        }

        result.sort((a, b) => {
            const aCurrent = a.patientId === patientId ? 0 : 1;
            const bCurrent = b.patientId === patientId ? 0 : 1;
            return aCurrent - bCurrent || new Date(b.invoiceDate).getTime() - new Date(a.invoiceDate).getTime();
        });

        return result;
    }, [allInvoices, patientId]);

    const filtered = useMemo(() => {
        if (!filter) return blocks;
        const lower = filter.toLowerCase();
        return blocks.filter(b =>
            b.patientName.toLowerCase().includes(lower) ||
            (b.invoiceNumber ?? '').toLowerCase().includes(lower) ||
            b.items.some(i =>
                i.description.toLowerCase().includes(lower) ||
                (i.number ?? '').toLowerCase().includes(lower)
            )
        );
    }, [blocks, filter]);

    const handleHide = () => {
        setFilter('');
        setExpandedRows({});
        onHide();
    };

    const rowExpansionTemplate = (block: BlockEntry) => (
        <DataTable value={block.items} size="small" className="p-2">
            <Column field="number" header="Ziffer" style={{width: '15%'}}/>
            <Column field="description" header="Beschreibung" style={{width: '60%'}}/>
            <Column header="Betrag" body={(i) => `${i.amount.toFixed(2)} €`} style={{width: '15%'}}/>
            <Column header="Anzahl" field="quantity" style={{width: '10%'}}/>
        </DataTable>
    );

    const handleSelect = (block: BlockEntry) => {
        onSelect(block.items);
        handleHide();
    };

    const rowClassName = (block: BlockEntry) =>
        block.patientId === patientId ? 'font-bold' : '';

    return (
        <Dialog
            header="Block laden"
            visible={visible}
            onHide={handleHide}
            style={{width: '70vw', maxWidth: '1000px'}}
        >
            <div className="flex flex-column gap-3">
                <InputText
                    placeholder="Nach Patient, Rechnungsnr. oder Ziffer/Beschreibung filtern..."
                    value={filter}
                    onChange={e => setFilter(e.target.value)}
                    className="w-full"
                />
                <DataTable
                    value={filtered}
                    dataKey="key"
                    selectionMode="single"
                    onRowSelect={e => handleSelect(e.data as BlockEntry)}
                    emptyMessage="Keine Blöcke gefunden."
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
                    <Column field="patientName" header="Patient" style={{width: '25%'}}/>
                    <Column field="invoiceNumber" header="Rechnungsnr." style={{width: '25%'}}/>
                    <Column
                        header="Behandlungsdatum"
                        body={(b: BlockEntry) => toGermanDateString(new Date(b.blockDate + 'T00:00:00'))}
                        style={{width: '25%'}}
                    />
                    <Column
                        header="Anzahl Positionen"
                        body={(b: BlockEntry) => b.items.length}
                        style={{width: '25%'}}
                    />
                </DataTable>
            </div>
        </Dialog>
    );
};
