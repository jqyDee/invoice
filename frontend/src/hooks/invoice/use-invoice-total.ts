import { useMemo } from 'react';
import { InvoiceType, type InvoiceItem, type InvoiceItemCreate } from '../../api';

/**
 * Berechnet die Gesamtsumme basierend auf dem Rechnungstyp.
 * KG: (Summe Einzelbeträge) * Anzahl Tage
 * HP: Summe (Betrag * Menge) pro Item
 */
export const useInvoiceTotal = (
    type: InvoiceType,
    items: (InvoiceItem | InvoiceItemCreate)[],
    dates: Date[]
) => {
    const isKG = type === InvoiceType.KG;

    return useMemo(() => {
        if (isKG) {
            const sumOfAmounts = items.reduce((acc, item) => acc + (item.amount || 0), 0);
            return sumOfAmounts * dates.length;
        } else {
            return items.reduce((acc, item) => acc + ((item.amount || 0) * (item.quantity || 1)), 0);
        }
    }, [items, dates, isKG]);
};