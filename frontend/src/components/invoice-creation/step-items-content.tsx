import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { OrderList } from "primereact/orderlist";
import { Dialog } from "primereact/dialog";
import {InvoiceType, type InvoiceItemCreate, type InvoiceDateCreate} from "../../api";
import { TreatmentForm } from "../treatment-form.tsx";
import {Tag} from "primereact/tag";
import {InvoiceCalendar} from "../invoice/invoice-calendar.tsx";
import {Header} from "../header.tsx";
import {Total} from "../total.tsx";
import {toLocalDateString} from "../../utilities/local-date-string.ts";
import {useInvoiceTotal} from "../../hooks/use-invoice-total.ts";

interface LocalInvoiceItem extends InvoiceItemCreate {
    id: number;
}

interface StepItemsProps {
    type: InvoiceType;
    dates: InvoiceDateCreate[];
    items: InvoiceItemCreate[];
    prev: (dates: InvoiceDateCreate[], items: InvoiceItemCreate[]) => void;
    next: (dates: InvoiceDateCreate[], items: InvoiceItemCreate[]) => void;
}

export const StepItemsContent: React.FC<StepItemsProps> = ({
                                                               type,
                                                               dates: initialDates,
                                                               items: initialItems,
                                                               prev,
                                                               next
}) => {
    const [dates, setDates] = useState<Date[]>(
        () => initialDates.map(d => new Date(d.date))
    );

    const [items, setItems] = useState<LocalInvoiceItem[]>(
        () => initialItems.map((item, index) => ({
            ...item,
            id: Date.now() + index
        }))
    );

    const [editingItem, setEditingItem] = useState<LocalInvoiceItem | undefined>(undefined);
    const [visible, setVisible] = useState<boolean>(false);

    const isKG = type === InvoiceType.KG;

    const openAddDialog = () => {
        setEditingItem(undefined);
        setVisible(true);
    };

    const openEditDialog = (item: LocalInvoiceItem) => {
        setEditingItem(item);
        setVisible(true);
    };

    const saveItem = (itemData: InvoiceItemCreate) => {
        if (editingItem) {
            setItems(prev => prev.map(i => i.id === editingItem.id ? { ...itemData, id: i.id } : i));
        } else {
            setItems(prev => [...prev, { ...itemData, id: Date.now() }]);
        }
        setVisible(false);
    };

    const removeItem = (id: number) => {
        setItems(prev => prev.filter(item => item.id !== id));
    };

    const handleSubmit = (forward: boolean) => {
        const cleanDates: InvoiceDateCreate[] = dates.map(d => ({
            date: toLocalDateString(d)
        }));

        const dateCount = cleanDates.length

        const cleanItems: InvoiceItemCreate[] = items.map(({ id, ...rest }) => {
            rest.quantity = isKG ? dateCount : 1;
            return rest;
        });

        if (forward) {
            next(cleanDates, cleanItems);
        } else {
            prev(cleanDates, cleanItems);
        }
    };

    const calculatedTotal = useInvoiceTotal(type, items, dates);

    const checkItem = (item: LocalInvoiceItem): boolean =>  {
        if (!isKG) {
            if (!item.number || !item.date) return true;
        }
        return false;
    }

    const checkItems = (): boolean => {
        let block: boolean = false;

        items.forEach(i => {
            if (checkItem(i)) block = true;
        });

        return block;
    }

    const itemTemplate = (item: LocalInvoiceItem) => (
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
                <Button icon="pi pi-trash" className="p-button-text p-button-danger p-button-rounded" onClick={() => removeItem(item.id)} />
            </div>
        </div>
    );

    return (
        <div className="flex flex-column gap-4">
            {/* Gemeinsamer Dialog für KG und HP */}
            <Dialog
                header={editingItem ? "Behandlung bearbeiten" : "Neue Behandlung"}
                visible={visible}
                style={{ width: '40vw' }}
                onHide={() => setVisible(false)}
            >
                <TreatmentForm
                    initialData={editingItem}
                    type={type}
                    onSave={saveItem}
                    onCancel={() => setVisible(false)}
                />
            </Dialog>

            {isKG && (
                <div className="col-12">
                    <InvoiceCalendar dates={dates} onChange={(e) => setDates(e.value as Date[])}/>
                </div>
            )}

            <div className="col-12">
                <Header title="Leistungen" />
                <OrderList
                    value={items}
                    onChange={(e) => setItems(e.value)}
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
                <Total total={calculatedTotal}/>
            </div>

            {/* Footer Navigation */}
            <div className="flex justify-content-between">
                <Button label="Zurück" icon="pi pi-arrow-left" className="p-button-text" onClick={() => handleSubmit(false)} />
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={items.length === 0 || (type === InvoiceType.KG && dates.length === 0) || checkItems()}
                    onClick={() => handleSubmit(true)}
                />
            </div>
        </div>
    );
};