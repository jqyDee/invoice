import {useMemo} from "react";
import {
    type DefaultInvoiceItem,
    type Invoice,
    type InvoiceCreate,
    type InvoiceUpdate,
} from "../../api";

export const useInvoiceItemDisplayItems = (
    invoice: Invoice | InvoiceCreate | InvoiceUpdate,
    allDefaults: DefaultInvoiceItem[] | undefined,
    readonly: boolean,
    isKG: boolean
) => {
    return useMemo(() => {
        const userItems = (invoice.user_items || []) as { description: string; amount: number; number?: string | null; quantity?: number }[];
        const coreItems = isKG
            ? userItems.map((item, i) => ({
                ...item,
                _tempId: `kg-${i}`,
                _originalIndex: i
            }))
            : (invoice.dates || []).flatMap((d) => {
                const date = (d as { date: string }).date;
                const items = (d as { items?: { description: string; amount: number; number?: string | null; quantity?: number }[] | null }).items;
                return items && items.length > 0
                    ? items.map((item, index) => ({
                        ...item,
                        date,
                        _tempId: `${date}-${index}`,
                        _originalIndex: index
                    }))
                    : [{
                        date,
                        isEmpty: true,
                        _tempId: `${date}-empty`,
                        description: '',
                        amount: 0,
                        _originalIndex: -1
                    }];
            }) || [];

        if (!readonly) return coreItems;

        const defaultItems = (invoice as Invoice).default_items;
        const defaultItemIds = (invoice as InvoiceCreate | InvoiceUpdate).default_item_ids;
        const activeDefaults = defaultItems ||
            (defaultItemIds && allDefaults
                ? allDefaults.filter(d => defaultItemIds.includes(d.default_item_id))
                : []);

        const dateCount = invoice.dates?.length || 1;
        const mapDefault = (d: DefaultInvoiceItem, prefix: string, i: number) => ({
            ...d,
            quantity: d.quantity ?? (isKG ? dateCount : 1),
            date: prefix,
            _tempId: `def-${prefix}-${i}`,
            _originalIndex: -1,
            isDefault: true
        });

        const prepend = activeDefaults.filter(d =>
            d.position === "PREPEND" || d.position === "BOTH").map((d, i) =>
            mapDefault(d, 'Standardleistungen (Vorher)', i)
        );
        const append = activeDefaults.filter(d =>
            d.position === "APPEND" || d.position === "BOTH").map((d, i) =>
            mapDefault(d, 'Standardleistungen (Nachher)', i)
        );

        return [...prepend, ...coreItems, ...append];
    }, [invoice, readonly, allDefaults, isKG]);
};
