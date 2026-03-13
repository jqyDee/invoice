import {type Invoice, type InvoiceItemCreate, InvoiceType, InvoiceStatus} from '../api';

export interface TemplateItem {
    description: string;
    amount: number;
    number?: string | null;
    quantity: number;
    patientId: number;
    patientName: string;
    invoiceId: number;
    invoiceDate: string;
}

export function extractTemplateItems(invoices: Invoice[], currentPatientId: number): TemplateItem[] {
    // Sort invoices newest-first so we keep the most recent occurrence when deduplicating
    const sorted = [...invoices].sort((a, b) =>
        new Date(b.invoice_date).getTime() - new Date(a.invoice_date).getTime()
    );

    const seen = new Set<string>();
    const items: TemplateItem[] = [];

    for (const invoice of sorted) {
        const patientName = `${invoice.patient.first_name} ${invoice.patient.last_name}`;
        const patientId = invoice.patient_id;

        const push = (item: { description: string; amount: number; number?: string | null; quantity?: number }) => {
            const key = `${item.description}|${item.amount}|${item.number ?? ''}`;
            if (seen.has(key)) return;
            seen.add(key);
            items.push({
                description: item.description,
                amount: item.amount,
                number: item.number,
                quantity: item.quantity ?? 1,
                patientId,
                patientName,
                invoiceId: invoice.invoice_id,
                invoiceDate: invoice.invoice_date,
            });
        };

        for (const item of invoice.user_items) push(item);
        for (const date of invoice.dates) {
            for (const item of date.items ?? []) push(item);
        }
    }

    items.sort((a, b) => {
        const aCurrent = a.patientId === currentPatientId ? 0 : 1;
        const bCurrent = b.patientId === currentPatientId ? 0 : 1;
        return aCurrent - bCurrent;
    });

    return items;
}

export function getLastKGInvoiceItems(invoices: Invoice[], patientId: number, invoiceType: InvoiceType = InvoiceType.KG): InvoiceItemCreate[] | null {
    const patientKGInvoices = invoices
        .filter(inv =>
            inv.patient_id === patientId &&
            inv.type === invoiceType &&
            inv.status !== InvoiceStatus.DRAFT
        )
        .sort((a, b) => new Date(b.invoice_date).getTime() - new Date(a.invoice_date).getTime());

    if (patientKGInvoices.length === 0) return null;

    const items = patientKGInvoices[0].user_items;
    if (items.length === 0) return null;

    return items.map(item => ({
        description: item.description,
        amount: item.amount,
        number: item.number,
        quantity: item.quantity,
    }));
}
