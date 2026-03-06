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
    const isKG = invoice.type === InvoiceType.KG;

    const [editingItem, setEditingItem] = useState<any>(undefined);
    const [prefillDate, setPrefillDate] = useState<string | undefined>(undefined);
    const [visible, setVisible] = useState(false);
    const [isDateDialogOpen, setIsDateDialogOpen] = useState(false);
    const [newDate, setNewDate] = useState<Date | null>(null);
    const [editingDate, setEditingDate] = useState<string | null>(null);
    const [editDateValue, setEditDateValue] = useState<Date | null>(null);
    const [isEditDateDialogOpen, setIsEditDateDialogOpen] = useState(false);

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
        if (isKG) {
            const items = [...(invoice.user_items || [])];
            editingItem ? items[items.findIndex(i => i === editingItem)] = formData : items.push(formData);
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
        if (isKG) onChange({ user_items: invoice.user_items!.filter((i: InvoiceItemCreate) => i !== item) });
        else {
            const dates = [...(invoice.dates || [])];
            dates.find(d => d.date === date)?.items!.splice(index!, 1);
            onChange({ dates });
        }
    };

    const addDate = () => {
        if (newDate && onChange) {
            const dateStr = toLocalDateString(newDate);
            const dates = [...(invoice.dates || [])];
            if (!dates.find(d => d.date === dateStr)) {
                dates.push({ date: dateStr, items: [] });
                dates.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
                onChange({ dates });
            }
            setIsDateDialogOpen(false);
            setNewDate(null);
        }
    };

    const removeDate = (date: string) => {
        onChange && onChange({ dates: invoice.dates!.filter((d: any) => d.date !== date) });
    };

    const openEditDate = (date: string) => {
        setEditingDate(date);
        setEditDateValue(new Date(date + 'T00:00:00'));
        setIsEditDateDialogOpen(true);
    };

    const changeDate = () => {
        if (!editDateValue || !editingDate || !onChange) return;
        const newDateStr = toLocalDateString(editDateValue);
        if (newDateStr === editingDate) {
            setIsEditDateDialogOpen(false);
            return;
        }
        const dates = [...(invoice.dates || [])] as any[];
        const oldIdx = dates.findIndex(d => d.date === editingDate);
        if (oldIdx === -1) return;
        const existingIdx = dates.findIndex(d => d.date === newDateStr);
        if (existingIdx !== -1) {
            dates[existingIdx] = { ...dates[existingIdx], items: [...(dates[existingIdx].items || []), ...(dates[oldIdx].items || [])] };
            dates.splice(oldIdx, 1);
        } else {
            dates[oldIdx] = { ...dates[oldIdx], date: newDateStr };
        }
        dates.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        onChange({ dates });
        setIsEditDateDialogOpen(false);
        setEditingDate(null);
        setEditDateValue(null);
    };

    return {
        state: { editingItem, prefillDate, visible, isDateDialogOpen, newDate, editingDate, editDateValue, isEditDateDialogOpen },
        setters: { setVisible, setIsDateDialogOpen, setNewDate, setEditDateValue, setIsEditDateDialogOpen },
        actions: { openEdit, openAdd, saveItem, removeItem, addDate, removeDate, openEditDate, changeDate }
    };
};
