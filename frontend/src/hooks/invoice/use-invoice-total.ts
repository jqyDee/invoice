import { useMemo } from 'react';

/**
 * Berechnet die Gesamtsumme der Rechnung.
 * - User-Items: amount × quantity (quantity=1 da kein Eingabefeld)
 * - Default-Items: amount × (quantity ?? Anzahl Tage)
 * Gilt für KG und HP gleichermaßen.
 */
export const useInvoiceTotal = (
    items: { amount: number; quantity?: number | null }[],
    dates: Date[]
) => {
    return useMemo(() => {
        const dateCount = Math.max(dates.length, 1);
        const total = items.reduce((acc, item) => {
            const qty = item.quantity ?? dateCount;
            return acc + (item.amount || 0) * qty;
        }, 0);
        return Math.round(total * 100) / 100;
    }, [items, dates]);
};