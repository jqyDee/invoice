import {Tag} from "primereact/tag";
import {Button} from "primereact/button";
import type {InvoiceItemCreate} from "../../api";

interface DisplayItem extends InvoiceItemCreate {
    isEmpty?: boolean;
    isDefault?: boolean;
    date?: string;
    _originalIndex: number;
}

interface ActionCellProps {
    item: DisplayItem;
    readonly: boolean;
    isKG: boolean;
    onEdit: (item: DisplayItem) => void;
    onDel: (date: string | undefined, item: DisplayItem, index?: number) => void;
}

export const ActionCell = ({ item, readonly, isKG, onEdit, onDel }: ActionCellProps) => {
    if (readonly || item.isEmpty || item.isDefault) return null;
    const isWarning = !isKG && (!item.number || !item.date);

    return (
        <div className="flex justify-content-end gap-1">
            {isWarning && <Tag severity="warning" icon="pi pi-exclamation-circle" rounded />}
            <Button
                icon="pi pi-pencil"
                className="p-button-text p-button-rounded"
                onClick={() => onEdit(item)}
            />
            <Button
                icon="pi pi-trash"
                className="p-button-text p-button-danger p-button-rounded"
                onClick={() => onDel(isKG ? undefined : item.date, item, isKG ? undefined : item._originalIndex)}
            />
        </div>
    );
};
