import React from "react";
import { useParams } from "react-router-dom";
import { enforceNonNull } from "../utilities/enforce-non-null.ts";
import { getPdfTherapyPdfTherapyPatientIdGetOptions } from "../api/@tanstack/react-query.gen.ts";
import {PdfPreviewViewer} from "../utilities/pdf-preview-viewer.tsx";

export const TherapyPreviewView: React.FC = () => {
    const { id } = useParams();

    const queryOptions = getPdfTherapyPdfTherapyPatientIdGetOptions({
        path: { patient_id: parseInt(enforceNonNull(id)) }
    });

    return <PdfPreviewViewer queryOptions={queryOptions} title="Therapie Preview" />;
};