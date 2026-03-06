import React, { useEffect, useState } from "react";
import { useQuery, type UseQueryOptions } from "@tanstack/react-query";
import { useGlobalToast } from "../hooks/use-global-toast.ts";

interface PdfPreviewViewerProps {
    queryOptions: UseQueryOptions<any, any, any, any>;
    title?: string;
}

export const PdfPreviewViewer: React.FC<PdfPreviewViewerProps> = ({
    queryOptions,
    title = "PDF Preview"
}) => {
    const { showToast } = useGlobalToast();
    const [pdfUrl, setPdfUrl] = useState<string | null>(null);

    const { data: pdfData, error, isLoading } = useQuery(queryOptions);

    useEffect(() => {
        if (error) {
            showToast({
                severity: 'error',
                summary: 'Fehler',
                // Cast to any to safely access your backend's specific .detail property
                detail: `PDF konnte nicht geladen werden. ${(error as any).detail || error.message}`,
                life: 5000
            });
        }
    }, [error, showToast]);

    useEffect(() => {
        if (pdfData) {
            const objectUrl = URL.createObjectURL(pdfData as Blob);
            setPdfUrl(objectUrl);

            return () => {
                URL.revokeObjectURL(objectUrl);
            };
        }
    }, [pdfData]);

    if (isLoading) {
        return (
            <div className="flex align-items-center justify-content-center flex-grow-1 h-screen">
                <i className="pi pi-spin pi-spinner" style={{ fontSize: '2rem' }}></i>
            </div>
        );
    }

    if (error) {
        return <div className="p-4 text-red-500">PDF konnte nicht geladen werden.</div>;
    }

    return (
        <div className="flex flex-column" style={{ height: 'calc(100vh - 70px)' }}>
            {pdfUrl && (
                <iframe
                    src={pdfUrl}
                    className="flex-grow-1 border-none w-full"
                    title={title}
                />
            )}
        </div>
    );
};