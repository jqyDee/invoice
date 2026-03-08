import { useMemo } from 'react';
import {InvoiceType} from "../../api";

/**
 * Berechnet die Gesamtsumme der Rechnung.
 * - User-Items: amount × quantity (quantity=1 da kein Eingabefeld)
 * - Default-Items: amount × (quantity ?? Anzahl Tage)
 * Gilt für KG und HP gleichermaßen.
 */
export const useInvoiceTotal = (
    items: { amount: number; quantity?: number | null }[],
    dates: Date[],
    type: InvoiceType
) => {
    return useMemo(() => {
        const dateCount = Math.max(dates.length, 1);
        console.log(type)
        const total = items.reduce((acc, item) => {
            const qty = type === InvoiceType.KG ? dateCount : 1;
            return acc + (item.amount || 0) * qty;
        }, 0);
        return Math.round(total * 100) / 100;
    }, [items, dates]);
};