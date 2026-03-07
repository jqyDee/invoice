import { useMemo } from 'react';
import { InvoiceType } from '../../api';

/**
 * Berechnet die Gesamtsumme basierend auf dem Rechnungstyp.
 * KG: Anzahl Tage * Summe Einzelbeträge (user + default items)
 * HP: Summe Einzelbeträge (user + default items)
 */
export const useInvoiceTotal = (
    type: InvoiceType,
    items: { amount: number }[],
    dates: Date[]
) => {
    const isKG = type === InvoiceType.KG;

    return useMemo(() => {
        const sumOfAmounts = items.reduce((acc, item) => acc + (item.amount || 0), 0);
        if (isKG) {
            return dates.length * sumOfAmounts;
        } else {
            return sumOfAmounts;
        }
    }, [items, dates, isKG]);
};