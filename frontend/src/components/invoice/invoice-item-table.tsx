import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Calendar } from 'primereact/calendar';
import { useQuery } from "@tanstack/react-query";
import {InvoiceType, type InvoiceCreate, type InvoiceUpdate, type Invoice, type InvoiceItemCreate} from '../../api';
import { getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions } from "../../api/@tanstack/react-query.gen.ts";
import { InvoiceTreatmentForm} from './invoice-treatment-form';
import { toGermanDateString} from '../../utilities/local-date-string';
import {useInvoiceItemDisplayItems} from "../../hooks/invoice/use-invoice-item-display.ts";
import {useInvoiceItemMutations} from "../../hooks/invoice/use-invoice-item-mutation.ts";
import React from "react";
import {ActionCell} from "./invoice-item-action-cell.tsx";

interface InvoiceItemTableProps {
    invoice: Invoice | InvoiceCreate | InvoiceUpdate;
    onChange?: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    readonly?: boolean;
}

export const InvoiceItemTable: React.FC<InvoiceItemTableProps> = ({ invoice, onChange, readonly = false }) => {
    const isKG = invoice.type === InvoiceType.KG;

    const { data: allDefaults } = useQuery({ ...getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({ query: { invoice_type: invoice.type } }), enabled: readonly });
    const displayItems = useInvoiceItemDisplayItems(invoice, allDefaults, readonly, isKG);
    const { state, setters, actions } = useInvoiceItemMutations(invoice, onChange);

    const headerTemplate = (data: any) => (
        <div className="flex align-items-center justify-content-between py-2">
            <div className="flex align-items-center gap-2 text-lg font-bold">
                <i className="pi pi-calendar text-primary"></i><span>{toGermanDateString(new Date(data.date ?? ''))}</span>
            </div>
            {!readonly && (
                <div className="flex gap-2">
                    <Button
                        icon="pi pi-plus"
                        label="Leistung"
                        className="p-button-rounded"
                        onClick={() => actions.openAdd(data.date)}
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
            {!readonly && (
                <>
                    <Dialog
                        header={state.editingItem ? "Behandlung bearbeiten" : "Neue Behandlung"}
                        visible={state.visible}
                        style={{ width: '40vw' }}
                        onHide={() => setters.setVisible(false)}
                    >
                        <InvoiceTreatmentForm
                            initialData={state.editingItem || (state.prefillDate ? { date: state.prefillDate } : null)}
                            type={invoice.type!}
                            onSave={actions.saveItem}
                            onCancel={() => setters.setVisible(false)}
                        />
                    </Dialog>
                    <Dialog
                        header={state.dateDialogMode === 'add' ? "Neues Behandlungsdatum" : "Datum ändern"}
                        visible={state.dateDialogMode !== null}
                        onHide={actions.closeDateDialog}
                        style={{ maxWidth: '90vw', minWidth: '30vw' }}
                    >
                        <div className="flex flex-column gap-3">
                            <Calendar
                                value={state.datePickerValue}
                                onChange={(e) => setters.setDatePickerValue(e.value as Date)}
                                inline
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
                                    onClick={actions.confirmDate}
                                    disabled={!state.datePickerValue}
                                />
                            </div>
                        </div>
                    </Dialog>
                </>
            )}

            {/* Tables */}
            {!isKG ? (
                <DataTable
                    value={displayItems}
                    rowGroupMode="subheader"
                    dataKey="_tempId"
                    groupRowsBy="date"
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
                        style={{ width: '15%' }}
                    />
                    <Column
                        field="description"
                        header="Beschreibung"
                        body={(d) => d.isEmpty
                            ? <span className="text-color-secondary italic">Keine Leistungen hinterlegt</span>
                            : d.description}
                        style={{ width: '50%' }}
                    />
                    <Column
                        field="amount"
                        header="Betrag"
                        body={(d) => d.isEmpty ? '' : `${d.amount.toFixed(2)} €`}
                        style={{ width: '15%' }}
                    />
                    {!readonly &&
                        <Column
                            header="Aktionen"
                            alignHeader="right"
                            body={(item) =>
                                <ActionCell
                                    item={item}
                                    isKG={isKG}
                                    readonly={readonly}
                                    onEdit={actions.openEdit}
                                    onDel={actions.removeItem}
                                    onMoveUp={actions.moveItemUp}
                                    onMoveDown={actions.moveItemDown}
                                />
                            }
                            style={{ width: '20%' }}
                        />
                    }
                </DataTable>
            ) : (
                <DataTable
                    value={displayItems}
                    onRowReorder={!readonly && onChange
                        ? (e) =>
                            onChange({ user_items: e.value as InvoiceItemCreate[] })
                        : undefined
                    }
                    className="custom-no-buttons"
                    emptyMessage="Keine Leistungen vorhanden."
                    stripedRows
                >
                    {!readonly &&
                        <Column rowReorder style={{ width: '3rem' }} />
                    }
                    <Column
                        field="description"
                        header="Beschreibung"
                        style={{ width: readonly ? '75%' : '62%' }}
                    />
                    <Column
                        field="amount"
                        header="Betrag"
                        body={(d) => `${d.amount.toFixed(2)} €`} style={{ width: '15%' }}
                    />
                    {!readonly &&
                        <Column body={(item) =>
                            <ActionCell
                                item={item}
                                isKG={isKG}
                                readonly={readonly}
                                onEdit={actions.openEdit}
                                onDel={actions.removeItem}
                            />
                        }
                                style={{ width: '20%' }}
                        />
                    }
                </DataTable>
            )}

            {/* Add Buttons */}
            {!readonly && !isKG &&
                <Button
                    label="Neues Datum hinzufügen"
                    icon="pi pi-calendar-plus"
                    className="p-button-outlined w-full"
                    onClick={actions.openAddDate}
                />
            }
            {!readonly && isKG &&
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