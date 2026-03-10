import {
    type Invoice,
    type InvoiceCreate,
    type InvoiceItemCreate,
    InvoiceType,
    type InvoiceUpdate
} from "../../api";
import {useState} from "react";
import type {TreatmentFormData} from "../../components/invoice/invoice-treatment-form.tsx";
import {toLocalDateString} from "../../utilities/local-date-string.ts";

export const useInvoiceItemMutations = (
    invoice: Invoice | InvoiceCreate | InvoiceUpdate,
    onChange?: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void
) => {
    const isKGorGT = invoice.type === InvoiceType.KG || invoice.type === InvoiceType.GT;

    const [editingItem, setEditingItem] = useState<any>(undefined);
    const [prefillDate, setPrefillDate] = useState<string | undefined>(undefined);
    const [visible, setVisible] = useState(false);

    // Unified date dialog state
    const [dateDialogMode, setDateDialogMode] = useState<'add' | 'edit' | null>(null);
    const [datePickerValue, setDatePickerValue] = useState<Date | null>(null);
    const [editingDate, setEditingDate] = useState<string | null>(null);

    const openEdit = (item: any) => {
        setEditingItem(item);
        setPrefillDate(undefined);
        setVisible(true);
    };
    const openAdd = (date?: string) => {
        setEditingItem(undefined);
        setPrefillDate(date);
        setVisible(true);
    };

    const saveItem = (formData: TreatmentFormData) => {
        if (!onChange) return;
        if (isKGorGT) {
            const items = [...(invoice.user_items || [])];
            if (editingItem) {
                const idx = editingItem._originalIndex ?? -1;
                if (idx >= 0) items[idx] = formData;
            } else {
                items.push(formData);
            }
            onChange({ user_items: items });
        } else {
            const dates = [...(invoice.dates || [])];
            const itemData = {
                description: formData.description,
                amount: formData.amount,
                number: formData.number,
                quantity: formData.quantity
            };

            if (editingItem && editingItem.date) {
                const oldDateIdx = dates.findIndex(d => d.date === editingItem.date);
                if (editingItem.date === formData.date) {
                    dates[oldDateIdx].items![editingItem._originalIndex] = itemData;
                } else {
                    dates[oldDateIdx].items!.splice(editingItem._originalIndex, 1);
                    const newDateIdx = dates.findIndex(d => d.date === formData.date);
                    newDateIdx !== -1 ? dates[newDateIdx].items!.push(itemData) : dates.push({ date: formData.date!, items: [itemData] });
                }
            } else {
                const targetIdx = dates.findIndex(d => d.date === formData.date);
                targetIdx !== -1 ? dates[targetIdx].items!.push(itemData) : dates.push({ date: formData.date!, items: [itemData] });
            }
            dates.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
            onChange({ dates });
        }
        setVisible(false);
    };

    const removeItem = (date: string | undefined, item: InvoiceItemCreate, index?: number) => {
        if (!onChange) return;
        if (isKGorGT) {
            const idx = (item as any)._originalIndex ?? -1;
            if (idx >= 0) {
                const items = [...(invoice.user_items || [])];
                items.splice(idx, 1);
                onChange({ user_items: items });
            }
        }
        else {
            const dates = [...(invoice.dates || [])];
            dates.find(d => d.date === date)?.items!.splice(index!, 1);
            onChange({ dates });
        }
    };

    const openAddDate = () => {
        setDatePickerValue(null);
        setDateDialogMode('add');
    };

    const openEditDate = (date: string) => {
        setEditingDate(date);
        const parsed = new Date(date + 'T00:00:00');
        setDatePickerValue(parsed.getFullYear() < 1000 ? new Date() : parsed);
        setDateDialogMode('edit');
    };

    const closeDateDialog = () => {
        setDateDialogMode(null);
        setDatePickerValue(null);
        setEditingDate(null);
    };

    const confirmDate = () => {
        if (!datePickerValue || !onChange) return;
        if (dateDialogMode === 'add') {
            const dateStr = toLocalDateString(datePickerValue);
            const dates = [...(invoice.dates || [])];
            if (!dates.find(d => d.date === dateStr)) {
                dates.push({ date: dateStr, items: [] });
                dates.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
                onChange({ dates });
            }
        } else if (dateDialogMode === 'edit' && editingDate) {
            const newDateStr = toLocalDateString(datePickerValue);
            if (newDateStr !== editingDate) {
                const dates = [...(invoice.dates || [])] as any[];
                const oldIdx = dates.findIndex(d => d.date === editingDate);
                if (oldIdx !== -1) {
                    const existingIdx = dates.findIndex(d => d.date === newDateStr);
                    if (existingIdx !== -1) {
                        dates[existingIdx] = { ...dates[existingIdx], items: [...(dates[existingIdx].items || []), ...(dates[oldIdx].items || [])] };
                        dates.splice(oldIdx, 1);
                    } else {
                        dates[oldIdx] = { ...dates[oldIdx], date: newDateStr };
                    }
                    dates.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
                    onChange({ dates });
                }
            }
        }
        closeDateDialog();
    };

    const removeDate = (date: string) => {
        onChange && onChange({ dates: invoice.dates!.filter((d: any) => d.date !== date) });
    };

    const moveItemUp = (date: string, index: number) => {
        if (!onChange || index === 0) return;
        const dates = [...(invoice.dates || [])] as any[];
        const dateIdx = dates.findIndex(d => d.date === date);
        if (dateIdx === -1) return;
        const items = [...dates[dateIdx].items];
        [items[index - 1], items[index]] = [items[index], items[index - 1]];
        dates[dateIdx] = { ...dates[dateIdx], items };
        onChange({ dates });
    };

    const moveItemDown = (date: string, index: number) => {
        if (!onChange) return;
        const dates = [...(invoice.dates || [])] as any[];
        const dateIdx = dates.findIndex(d => d.date === date);
        if (dateIdx === -1) return;
        const items = [...dates[dateIdx].items];
        if (index >= items.length - 1) return;
        [items[index], items[index + 1]] = [items[index + 1], items[index]];
        dates[dateIdx] = { ...dates[dateIdx], items };
        onChange({ dates });
    };

    return {
        state: { editingItem, prefillDate, visible, dateDialogMode, datePickerValue },
        setters: { setVisible, setDatePickerValue },
        actions: { openEdit, openAdd, saveItem, removeItem, openAddDate, removeDate, openEditDate, confirmDate, closeDateDialog, moveItemUp, moveItemDown }
    };
};
