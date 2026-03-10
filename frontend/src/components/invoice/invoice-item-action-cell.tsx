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
    isKGorGT: boolean;
    onEdit: (item: DisplayItem) => void;
    onDel: (date: string | undefined, item: DisplayItem, index?: number) => void;
    onMoveUp?: (date: string, index: number) => void;
    onMoveDown?: (date: string, index: number) => void;
}

export const ActionCell = ({ item, readonly, isKGorGT, onEdit, onDel, onMoveUp, onMoveDown }: ActionCellProps) => {
    if (readonly || item.isEmpty || item.isDefault) return null;
    const isWarning = !isKGorGT && (!item.number || !item.date);

    return (
        <div className="flex flex-column md:flex-row justify-content-end gap-1">
            {isWarning && <Tag severity="warning" icon="pi pi-exclamation-circle" rounded />}
            <div className="flex">
                {!isKGorGT && onMoveUp && (
                    <Button
                        icon="pi pi-angle-up"
                        className="p-button-text p-button-rounded p-button-sm"
                        onClick={() => onMoveUp(item.date!, item._originalIndex)}
                    />
                )}
                {!isKGorGT && onMoveDown && (
                    <Button
                        icon="pi pi-angle-down"
                        className="p-button-text p-button-rounded p-button-sm"
                        onClick={() => onMoveDown(item.date!, item._originalIndex)}
                    />
                )}
            </div>
            <div className="flex">
                <Button
                    icon="pi pi-pencil"
                    className="p-button-text p-button-rounded"
                    onClick={() => onEdit(item)}
                />
                <Button
                    icon="pi pi-trash"
                    className="p-button-text p-button-danger p-button-rounded"
                    onClick={() => onDel(isKGorGT ? undefined : item.date, item, isKGorGT ? undefined : item._originalIndex)}
                />
            </div>
        </div>
    );
};
