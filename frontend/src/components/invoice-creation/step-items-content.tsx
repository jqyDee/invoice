import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { OrderList } from "primereact/orderlist";
import { Dialog } from "primereact/dialog";
import {
    InvoiceType,
    type InvoiceItemCreate,
    type InvoiceCreate, type InvoiceUpdate, type InvoiceItemUpdate, type DefaultInvoiceItem
} from "../../api";
import { InvoiceTreatmentForm } from "../invoice/invoice-treatment-form.tsx";
import {Tag} from "primereact/tag";
import {InvoiceCalendar} from "../invoice/invoice-calendar.tsx";
import {Header} from "../../utilities/header.tsx";
import {Total} from "../../utilities/total.tsx";
import {useInvoiceTotal} from "../../hooks/use-invoice-total.ts";
import {useQuery} from "@tanstack/react-query";
import {getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions} from "../../api/@tanstack/react-query.gen.ts";
import {enforceNonNull} from "../../utilities/enforce-non-null.ts";
import {toLocalDateString} from "../../utilities/local-date-string.ts";
import {InputSwitch} from "primereact/inputswitch";
import {Fieldset} from "primereact/fieldset";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";

interface StepItemsProps {
    invoice: InvoiceCreate | InvoiceUpdate
    onChange: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    prev: () => void;
    next: () => void;
}

export const StepItemsContent: React.FC<StepItemsProps> = ({ invoice, onChange, prev, next }) => {
    const [editingItem, setEditingItem] = useState<InvoiceItemCreate | InvoiceItemUpdate | undefined>(undefined);
    const [visible, setVisible] = useState<boolean>(false);

    const { data: availableDefaults } = useQuery(getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
        query: { invoice_type: invoice.type }
    }));

    const isKG = invoice.type === InvoiceType.KG;

    const openAddDialog = () => {
        setEditingItem(undefined);
        setVisible(true);
    };

    const openEditDialog = (item: InvoiceItemCreate | InvoiceItemUpdate) => {
        setEditingItem(item);
        setVisible(true);
    };

    const toggleDefault = (id: number) => {
        const currentIds = invoice.default_item_ids || [];
        console.log(invoice.default_item_ids)
        const nextIds = currentIds.includes(id)
            ? currentIds.filter(i => i !== id)
            : [...currentIds, id];
        console.log(nextIds)
        onChange({ default_item_ids: nextIds });
        console.log(invoice.default_item_ids)
    };

    const saveUserItem = (itemData: InvoiceItemCreate) => {
        const currentItems = [...(invoice.user_items || [])];
        if (editingItem) {
            const index = currentItems.findIndex(i => i === editingItem);
            if (index !== -1) {
                currentItems[index] = itemData;
            }
        } else {
            currentItems.push(itemData);
        }
        onChange({ user_items: currentItems });
        setVisible(false);
    };

    const removeUserItem = (index: number) => {
        const currentItems = invoice.user_items?.filter((_, i) => i !== index);
        onChange({ user_items: currentItems });
    };

    const calculatedTotal = useInvoiceTotal(
        enforceNonNull(invoice.type),
        enforceNonNull(invoice.user_items),
        enforceNonNull(invoice.dates).map(d => new Date(d.date))
    );

    const checkItem = (item: InvoiceItemCreate | InvoiceItemUpdate): boolean =>  {
        if (!isKG) {
            if (!item.number || !item.date) return true;
        }
        return false;
    }

    const itemTemplate = (item: InvoiceItemCreate | InvoiceItemUpdate) => {
        const index = invoice.user_items?.indexOf(item) ?? -1;

        return (
            <div className="grid w-full align-items-center p-2">
                {!isKG &&
                    <div className="col-2">
                        <span className="text-lg">{item.date}</span>
                        {(item.number && !isKG) && <small className="block text-color-secondary">Ziffer: {item.number}</small>}
                    </div>
                }
                <div className={isKG ? "col-8" : "col-6"}>
                    <span className="text-lg">{item.description}</span>
                </div>
                <div className="col-2 text-right font-semibold">
                    {item.amount.toFixed(2)} €
                </div>
                <div className="col-2 flex justify-content-end gap-1">
                    {checkItem(item) && <Tag severity="warning" icon="pi pi-exclamation-circle" className="" rounded/>}
                    <Button icon="pi pi-pencil" className="p-button-text p-button-rounded" onClick={() => openEditDialog(item)} />
                    <Button icon="pi pi-trash" className="p-button-text p-button-danger p-button-rounded" onClick={() => removeUserItem(index)} />
                </div>
            </div>
        )
    };

    return (
        <div className="flex flex-column gap-4">
            {/* Gemeinsamer Dialog für KG und HP */}
            <Dialog
                header={editingItem ? "Behandlung bearbeiten" : "Neue Behandlung"}
                visible={visible}
                style={{ width: '40vw' }}
                onHide={() => setVisible(false)}
            >
                <InvoiceTreatmentForm
                    initialData={editingItem}
                    type={invoice.type!}
                    onSave={saveUserItem}
                    onCancel={() => setVisible(false)}
                />
            </Dialog>

            {isKG && (
                <div className="col-12">
                    <InvoiceCalendar
                        dates={invoice.dates?.map(d => new Date(d.date)) || []}
                        onChange={(e) => onChange({
                            dates: (e.value as Date[]).map(d => ({ date: toLocalDateString(d) }))
                        })}
                    />
                </div>
            )}

            <div className="col-12">
                <Header title="Leistungen" />
                <OrderList
                    value={invoice.user_items || []}
                    onChange={(e) => onChange({ user_items: e.value })}
                    itemTemplate={itemTemplate}
                    dataKey="id"
                    dragdrop
                    listStyle={{ height: '25rem' }}
                    className="custom-no-buttons p-orderlist-striped"
                />
                <Button
                    label="Behandlungsart hinzufügen"
                    icon="pi pi-plus"
                    className="p-button-outlined w-full mt-3"
                    onClick={openAddDialog}
                />

                <Fieldset
                    legend={
                        <div className="flex align-items-center gap-2">
                            <span>Standard-Leistungen</span>
                            {invoice.default_item_ids && (
                                <Tag value={invoice.default_item_ids.length} severity="info" rounded />
                            )}
                        </div>
                    }
                    toggleable
                    collapsed={true}
                    className="mt-4"
                >
                    <DataTable
                        value={availableDefaults}
                        key={`defaults-table-${invoice.default_item_ids?.length || 0}`}
                        showGridlines
                        className="p-datatable-sm p-datatable-striped w-full"
                    >
                        <Column
                            header="Beschreibung"
                            field="description"
                        />
                        <Column
                            header="Aktiv"
                            body={(i: DefaultInvoiceItem) =>
                                <InputSwitch
                                    checked={invoice.default_item_ids?.includes(i.default_item_id) || false}
                                    onChange={() => toggleDefault(i.default_item_id)}
                                />
                            }/>
                    </DataTable>
                </Fieldset>
            </div>


            <Total total={calculatedTotal}/>

            {/* Footer Navigation */}
            <div className="flex justify-content-between">
                <Button label="Zurück" icon="pi pi-arrow-left" className="p-button-text" onClick={prev} />
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={(invoice.user_items?.length === 0 && invoice.default_item_ids?.length === 0) || (isKG && invoice.dates?.length === 0)}
                    onClick={next}
                />
            </div>
        </div>
    );
};