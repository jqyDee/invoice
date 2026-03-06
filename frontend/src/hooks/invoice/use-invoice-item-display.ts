import {useMemo} from "react";

export const useInvoiceItemDisplayItems = (
    invoice: any,
    allDefaults: any[] | undefined,
    readonly: boolean,
    isKG: boolean
) => {
    return useMemo(() => {
        let coreItems = isKG
            ? (invoice.user_items || []).map((item: any, i: number) => ({
                ...item,
                _tempId: `kg-${i}`,
                _originalIndex: i
            }))
            : invoice.dates?.flatMap((d: any) => d.items?.length > 0
            ? d.items.map((item: any, index: number) => ({
                ...item,
                date: d.date,
                _tempId: `${d.date}-${index}`,
                _originalIndex: index
            }))
            : [{
                date: d.date,
                isEmpty: true,
                _tempId: `${d.date}-empty`,
                description: '',
                amount: 0,
                _originalIndex: -1
            }]) || [];

        if (!readonly) return coreItems;

        let activeDefaults = invoice.default_items ||
            (invoice.default_item_ids && allDefaults
                ? allDefaults.filter((d: any) =>
                    invoice.default_item_ids.includes(d.default_item_id))
                : []);

        const dateCount = invoice.dates?.length || 1;
        const mapDefault = (d: any, prefix: string, i: number) => ({
            ...d,
            quantity: d.quantity ?? (isKG ? dateCount : 1),
            date: prefix,
            _tempId: `def-${prefix}-${i}`,
            _originalIndex: -1,
            isDefault: true
        });

        const prepend = activeDefaults.filter((d: any) =>
            d.position === "PREPEND" || d.position === "BOTH").map((d: any, i: number) =>
            mapDefault(d, 'Standardleistungen (Vorher)', i)
        );
        const append = activeDefaults.filter((d: any) =>
            d.position === "APPEND" || d.position === "BOTH").map((d: any, i: number) =>
            mapDefault(d, 'Standardleistungen (Nachher)', i)
        );

        return [...prepend, ...coreItems, ...append];
    }, [invoice, readonly, allDefaults, isKG]);
};
