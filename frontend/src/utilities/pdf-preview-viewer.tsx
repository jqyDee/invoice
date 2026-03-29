import React, { useEffect, useState } from "react";
import { useQuery, type UseQueryOptions } from "@tanstack/react-query";
import { useGlobalToast } from "../hooks/use-global-toast.ts";
import { Button } from "primereact/button";
import {extractApiError} from "./api-error.ts";
import {useIsMobile} from "../hooks/use-is-mobile.ts";

interface PdfPreviewViewerProps {
    queryOptions: UseQueryOptions<any, any, any, any>;
    title?: string;
}

export const PdfPreviewViewer: React.FC<PdfPreviewViewerProps> = ({
                                                                      queryOptions,
                                                                      title = "PDF Preview"
                                                                  }) => {
    const {showToast} = useGlobalToast();
    const [pdfUrl, setPdfUrl] = useState<string | null>(null);
    const isMobile = useIsMobile();

    const {data: pdfData, error, isLoading} = useQuery({
        ...queryOptions,
        staleTime: 0,             // Always consider the data stale instantly
        gcTime: 0,                // Garbage collect immediately (React Query v5)
                                  // Note: Use `cacheTime: 0` if you are on React Query v4
        // refetchOnMount: 'always', // Always fetch a fresh PDF when opening the view
        // refetchOnWindowFocus: true // Refetch if they alt-tab away and come back
    });

    useEffect(() => {
        if (error) {
            showToast({
                severity: 'error',
                summary: 'Fehler',
                detail: `PDF konnte nicht geladen werden. ${extractApiError(error)}`,
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
                <i className="pi pi-spin pi-spinner" style={{fontSize: '2rem'}}></i>
            </div>
        );
    }

    if (error) {
        return <div className="p-4 text-red-500">PDF konnte nicht geladen werden.</div>;
    }

    if (isMobile) {
        return (
            <div className="flex flex-column align-items-center justify-content-center gap-3" style={{ height: 'calc(100vh - 70px)' }}>
                <i className="pi pi-file-pdf" style={{ fontSize: '4rem', color: 'var(--primary-color)' }} />
                <p className="m-0 text-600">PDF-Vorschau ist auf Mobilgeräten nicht verfügbar.</p>
                {pdfUrl && (
                    <a href={pdfUrl} target="_blank" rel="noreferrer" download>
                        <Button label="PDF öffnen" icon="pi pi-download" />
                    </a>
                )}
            </div>
        );
    }

    return (
        <div className="flex flex-column" style={{height: 'calc(100vh - 70px)'}}>
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