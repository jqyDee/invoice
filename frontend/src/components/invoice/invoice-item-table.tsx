import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {Button} from 'primereact/button';
import {Dialog} from 'primereact/dialog';
import {useQuery} from "@tanstack/react-query";
import {InvoiceType, type InvoiceCreate, type InvoiceUpdate, type Invoice, type InvoiceItemCreate} from '../../api';
import {getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions} from "../../api/@tanstack/react-query.gen.ts";
import {InvoiceTreatmentForm} from './invoice-treatment-form';
import {toGermanDateString, toLocalDateString} from '../../utilities/local-date-string';
import {useInvoiceItemDisplayItems} from "../../hooks/invoice/use-invoice-item-display.ts";
import {useInvoiceItemMutations} from "../../hooks/invoice/use-invoice-item-mutation.ts";
import React, {useState} from "react";
import {ActionCell} from "./invoice-item-action-cell.tsx";
import {InvoiceItemTemplatePanel} from "./invoice-item-template-panel.tsx";
import {InvoiceBlockTemplatePicker} from "./invoice-block-template-picker.tsx";
import type {TreatmentFormData} from "./invoice-treatment-form.tsx";
import {InputText} from "primereact/inputtext";
import {Calendar} from "primereact/calendar";

interface InvoiceItemTableProps {
    invoice: Invoice | InvoiceCreate | InvoiceUpdate;
    onChange?: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    readonly?: boolean;
    patientId?: number;
}

export const InvoiceItemTable: React.FC<InvoiceItemTableProps> = ({invoice, onChange, readonly = false, patientId}) => {
    const isKGorGT = invoice.type === InvoiceType.KG || invoice.type === InvoiceType.GT;

    const {data: allDefaults} = useQuery({
        ...getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({query: {invoice_type: invoice.type}}),
        enabled: readonly
    });
    const displayItems = useInvoiceItemDisplayItems(invoice, allDefaults, readonly, isKGorGT);
    const {state, setters, actions} = useInvoiceItemMutations(invoice, onChange);

    const [templateInitialData, setTemplateInitialData] = useState<Partial<TreatmentFormData> | null>(null);
    const [formKey, setFormKey] = useState(0);
    const [blockPickerDate, setBlockPickerDate] = useState<string | null>(null);

    const headerTemplate = (data: any) => (
        <div className="flex flex-column md:flex-row md:align-items-center md:justify-content-between py-2 gap-3">
            <div className="flex align-items-center gap-2 text-lg font-bold">
                <i className="pi pi-calendar text-primary"></i><span>{toGermanDateString(new Date((data.date ?? '') + 'T00:00:00'))}</span>
            </div>
            {!readonly && (
                <div className="flex flex-wrap gap-2">
                    <Button
                        icon="pi pi-plus"
                        label="Leistung"
                        className="p-button-rounded"
                        onClick={() => actions.openAdd(data.date)}
                    />
                    <Button
                        icon="pi pi-clone"
                        label="Block laden"
                        className="p-button-rounded p-button-outlined"
                        onClick={() => setBlockPickerDate(data.date)}
                    />
                    <Button
                        icon="pi pi-pencil"
                        className="p-button-rounded p-button-text"
                        onClick={() => actions.openEditDate(data.date)}
                    />
                    <Button
                        icon="pi pi-trash"
                        className="p-button-rounded p-button-danger"
                        onClick={() => actions.removeDate(data.date)}
                    />
                </div>
            )}
        </div>
    );

    return (
        <div className="flex flex-column gap-3 w-full">
            {/* Dialogs */}
            {!readonly && !isKGorGT && patientId && (
                <InvoiceBlockTemplatePicker
                    visible={blockPickerDate !== null}
                    onHide={() => setBlockPickerDate(null)}
                    patientId={patientId}
                    onSelect={(items) => {
                        const dates = [...(invoice.dates || [])] as any[];
                        const idx = dates.findIndex(d => d.date === blockPickerDate);
                        if (idx !== -1) {
                            dates[idx] = {...dates[idx], items};
                            onChange?.({dates});
                        }
                        setBlockPickerDate(null);
                    }}
                />
            )}
            {!readonly && (
                <>
                    <Dialog
                        header={state.editingItem ? "Behandlung bearbeiten" : "Neue Behandlung"}
                        visible={state.visible}
                        style={{maxWidth: '80vw'}}
                        onHide={() => {
                            setters.setVisible(false);
                            setTemplateInitialData(null);
                        }}
                    >
                        {!state.editingItem && patientId && (
                            <InvoiceItemTemplatePanel
                                patientId={patientId}
                                invoiceType={invoice.type!}
                                onSelect={(item) => {
                                    setTemplateInitialData(state.prefillDate ? {
                                        ...item,
                                        date: state.prefillDate
                                    } : item);
                                    setFormKey(k => k + 1);
                                }}
                            />
                        )}
                        <InvoiceTreatmentForm
                            key={formKey}
                            initialData={templateInitialData || state.editingItem || (state.prefillDate ? {date: state.prefillDate} : null)}
                            type={invoice.type!}
                            onSave={actions.saveItem}
                            onCancel={() => {
                                setters.setVisible(false);
                                setTemplateInitialData(null);
                            }}
                        />
                    </Dialog>
                    <Dialog
                        header={state.dateDialogMode === 'add' ? "Neues Behandlungsdatum" : "Datum ändern"}
                        visible={state.dateDialogMode !== null}
                        onHide={actions.closeDateDialog}
                        style={{minWidth: '30vw'}}
                    >
                        <div className="flex flex-column gap-3">
                            <Calendar
                                value={state.dateValue ? new Date(state.dateValue + 'T00:00:00') : new Date()}
                                onChange={(e) => setters.setDateValue(toLocalDateString(e.value as Date))}
                                inline
                                className="w-full"
                            />
                            <InputText
                                value={state.dateValue || ''}
                                onChange={(e) => setters.setDateValue(e.target.value)}
                                type="date"
                                className="w-full"
                            />

                            <div className="flex justify-content-end gap-2">
                                <Button
                                    label="Abbrechen"
                                    className="p-button-text"
                                    onClick={actions.closeDateDialog}
                                />
                                <Button
                                    label={state.dateDialogMode === 'add' ? "Hinzufügen" : "Speichern"}
                                    icon="pi pi-save"
                                    onClick={actions.confirmDate}
                                    disabled={!state.dateValue}
                                />
                            </div>
                        </div>
                    </Dialog>
                </>
            )}

            {/* Tables */}
            {!isKGorGT ? (
                <DataTable
                    value={displayItems}
                    rowGroupMode="subheader"
                    dataKey="_tempId"
                    groupRowsBy="date"
                    sortField="date"
                    sortOrder={1}
                    rowGroupHeaderTemplate={headerTemplate}
                    className="custom-no-buttons"
                    emptyMessage="Keine Behandlungsdaten vorhanden."
                    stripedRows
                    size="small"
                    showGridlines
                >
                    <Column
                        field="number"
                        header="Ziffer"
                        body={(d) => d.isEmpty ? '' : d.number}
                        style={{width: '10%'}}
                    />
                    <Column
                        field="description"
                        header="Beschreibung"
                        body={(d) => d.isEmpty
                            ? <span className="text-color-secondary italic">Keine Leistungen hinterlegt</span>
                            : d.description}
                        style={{width: '70%'}}
                    />
                    <Column
                        field="amount"
                        header="Betrag"
                        align="right"
                        body={(d) =>
                            <span className="align-items-end">{d.isEmpty ? '' : `${d.amount.toFixed(2)} €`}</span>
                        }
                        style={{width: '10%'}}
                    />
                    {!readonly &&
                        <Column
                            header="Aktionen"
                            alignHeader="right"
                            body={(item) =>
                                <ActionCell
                                    item={item}
                                    isKGorGT={isKGorGT}
                                    readonly={readonly}
                                    onEdit={actions.openEdit}
                                    onDel={actions.removeItem}
                                    onMoveUp={actions.moveItemUp}
                                    onMoveDown={actions.moveItemDown}
                                />
                            }
                            style={{width: '10%'}}
                        />
                    }
                </DataTable>
            ) : (
                <DataTable
                    value={displayItems}
                    onRowReorder={!readonly && onChange
                        ? (e) =>
                            onChange({user_items: e.value as InvoiceItemCreate[]})
                        : undefined
                    }
                    className="custom-no-buttons"
                    emptyMessage="Keine Leistungen vorhanden."
                    stripedRows
                >
                    {!readonly &&
                        <Column rowReorder style={{width: '3rem'}}/>
                    }
                    <Column
                        field="description"
                        header="Beschreibung"
                        style={{width: readonly ? '75%' : '62%'}}
                    />
                    <Column
                        field="amount"
                        header="Betrag"
                        body={(d) => `${d.amount.toFixed(2)} €`} style={{width: '15%'}}
                    />
                    {!readonly &&
                        <Column body={(item) =>
                            <ActionCell
                                item={item}
                                isKGorGT={isKGorGT}
                                readonly={readonly}
                                onEdit={actions.openEdit}
                                onDel={actions.removeItem}
                            />
                        }
                                style={{width: '20%'}}
                        />
                    }
                </DataTable>
            )}

            {/* Add Buttons */}
            {!readonly && !isKGorGT &&
                <Button
                    label="Neues Datum hinzufügen"
                    icon="pi pi-calendar-plus"
                    className="p-button-outlined w-full"
                    onClick={actions.openAddDate}
                />
            }
            {!readonly && isKGorGT &&
                <Button
                    label="Behandlungsart hinzufügen"
                    icon="pi pi-plus"
                    className="p-button-outlined w-full"
                    onClick={() => actions.openAdd()}
                />
            }
        </div>
    );
};