import {DefaultInvoiceItemPosition} from "../api";

export const toGermanDefaultPosition = (position: DefaultInvoiceItemPosition): string => {
    let defaultPositionString: string;

    switch (position) {
        case DefaultInvoiceItemPosition.PREPEND:
            defaultPositionString = "Vorne";
            break
        case DefaultInvoiceItemPosition.APPEND:
            defaultPositionString = "Hinten";
            break
        case DefaultInvoiceItemPosition.BOTH:
            defaultPositionString = "Vorne & Hinten";
            break
        default:
            defaultPositionString = position;
    }

    return defaultPositionString;
}
