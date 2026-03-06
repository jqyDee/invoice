import React from "react";
import { useParams } from "react-router-dom";
import { enforceNonNull } from "../utilities/enforce-non-null.ts";
import { getPdfInvoicePdfInvoiceInvoiceIdGetOptions } from "../api/@tanstack/react-query.gen.ts";
import {PdfPreviewViewer} from "../utilities/pdf-preview-viewer.tsx";

export const InvoicePreviewView: React.FC = () => {
    const { id } = useParams();

    const queryOptions = getPdfInvoicePdfInvoiceInvoiceIdGetOptions({
        path: { invoice_id: parseInt(enforceNonNull(id)) }
    });

    return <PdfPreviewViewer queryOptions={queryOptions} title="Rechnung Preview" />;
};