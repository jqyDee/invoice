import React from "react";
import {useParams} from "react-router-dom";
import {enforceNonNull} from "../utilities/enforce-non-null.ts";
import {getPdfPrivacyPdfPrivacyPatientIdGetOptions} from "../api/@tanstack/react-query.gen.ts";
import {PdfPreviewViewer} from "../utilities/pdf-preview-viewer.tsx";

export const PrivacyPreviewView: React.FC = () => {
    const {id} = useParams();

    const queryOptions = getPdfPrivacyPdfPrivacyPatientIdGetOptions({
        path: {patient_id: parseInt(enforceNonNull(id))}
    });

    return <PdfPreviewViewer queryOptions={queryOptions} title="Datenschutz Preview"/>;
};
