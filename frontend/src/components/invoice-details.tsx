import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {
    deleteInvoiceInvoicesInvoiceIdDeleteMutation,
    getInvoiceInvoicesInvoiceIdGetOptions, getInvoicesInvoicesGetQueryKey,
} from "../api/@tanstack/react-query.gen.ts";
import {useNavigate, useParams} from "react-router-dom";
import React from "react";
import {StepOverviewContent} from "./invoice-creation/step-overview-content.tsx";
import {Button} from "primereact/button";
import {useGlobalToast} from "../contexts/toast.tsx";
import {ConfirmDialog, confirmDialog} from "primereact/confirmdialog";
import {ROUTES} from "../config/routes.ts";

export const InvoiceDetails: React.FC = () => {
    const {id} = useParams();
    const queryClient = useQueryClient();
    const {showToast} = useGlobalToast();
    const navigate = useNavigate();

    if (!id) {
        return <span>Rechnung konnte nicht geladen werden!</span>
    }

    const deleteMutation = useMutation({
        ...deleteInvoiceInvoicesInvoiceIdDeleteMutation(),
        onSuccess: async () => {
            showToast({ severity: 'success', summary: 'Fertig!', detail: 'Rechnung wurde gelöscht.', life: 3000});
            await queryClient.invalidateQueries({
                queryKey: getInvoicesInvoicesGetQueryKey()
            })
            navigate(-1);
        }
    })

    const {data: invoice} = useQuery(getInvoiceInvoicesInvoiceIdGetOptions({
        path: {invoice_id: id}
    }));

    if (!invoice) {
        return <span>Rechnung konnte nicht geladen werden!</span>
    }

    const accept = async () => {
        await deleteMutation.mutateAsync({
            path: {invoice_id: invoice.invoice_id.toString()}
        });
    }

    const confirm = () => {
        if (!invoice) {
            return;
        }

        confirmDialog({
            message: `Willst du die Rechnung ${invoice.invoice_number ? invoice.invoice_number : "/ Entwurf"} löschen?`,
            header: 'Löschen?',
            icon: 'pi pi-info-circle',
            defaultFocus: 'reject',
            acceptClassName: 'p-button-danger',
            rejectLabel: "Nein",
            acceptLabel: "Ja",
            accept,
            reject: () => {}

        })
    }

    return (
        <>
            <ConfirmDialog/>
            <StepOverviewContent
                header={<h1 className="text-4xl font-bold">Rechnung {invoice.invoice_number}</h1>}
                type={invoice.type}
                invoiceDate={invoice.invoice_date}
                invoiceNumber={invoice.invoice_number ?? '-'}
                isDraft={invoice.is_draft}
                patient={invoice.patient}
                items={invoice.items ?? []}
                dates={invoice.dates.map(d => new Date(d.date))}
                diagnosis={invoice.diagnosis ?? ''}
                isPreview={false}
                footer={
                    <div className="flex justify-content-between mt-2 gap-2">
                        <div className="flex gap-2">
                            <Button label="Löschen" icon="pi pi-trash" className="p-button-danger p-button-rounded" onClick={confirm}/>
                            <Button label="Bearbeiten" icon="pi pi-pencil" className="p-button-text p-button-rounded" onClick={() => console.log("Edit")}/>
                        </div>
                        <Button
                            label="PDF anzeigen"
                            icon="pi pi-file-pdf"
                            className="p-button-rounded"
                            onClick={() => navigate(ROUTES.INVOICE_PREVIEW.replace(':id', invoice.invoice_id.toString()))}
                        />
                    </div>
                }
            />
        </>
    );
}