import {InvoiceStatus} from "../api";

export const toGermanStatus = (status: InvoiceStatus): string => {
    let statusString: string = "";

    switch (status) {
        case InvoiceStatus.DRAFT:
            statusString = "Entwurf"
            break
        case InvoiceStatus.SAVED:
            statusString = "Gespeichert"
            break
        case InvoiceStatus.PAYMENT_DUE:
            statusString = "Herausgegeben"
            break
        case InvoiceStatus.PAID:
            statusString = "Bezahlt"
            break
    }

    return statusString;
}

type severity = 'success' | 'info' | 'warning' | 'danger' | 'secondary' | 'contrast' | null | undefined;

export const toSeverityStatus = (status: InvoiceStatus): severity => {
    let severityString: severity = null;

    switch (status) {
        case InvoiceStatus.DRAFT:
            severityString = "info"
            break
        case InvoiceStatus.SAVED:
            severityString = "secondary"
            break
        case InvoiceStatus.PAYMENT_DUE:
            severityString = "warning"
            break
        case InvoiceStatus.PAID:
            severityString = "success"
            break
    }

    return severityString;
}
