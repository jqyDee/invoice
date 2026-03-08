import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {
    deleteInvoiceInvoicesInvoiceIdDeleteMutation,
    getInvoiceInvoicesInvoiceIdGetOptions, getInvoicesInvoicesGetQueryKey,
} from "../api/@tanstack/react-query.gen.ts";
import {generatePath, useNavigate, useParams} from "react-router-dom";
import React from "react";
import {StepOverviewContent} from "./invoice-edit/step-overview-content.tsx";
import {Button} from "primereact/button";
import {ConfirmDialog, confirmDialog} from "primereact/confirmdialog";
import {ROUTES} from "../config/routes.ts";
import {enforceNonNull} from "../utilities/enforce-non-null.ts";
import {useGlobalToast} from "../hooks/use-global-toast.ts";

export const InvoiceDetailsView: React.FC = () => {
    const {id} = useParams();
    const queryClient = useQueryClient();
    const {showToast} = useGlobalToast();
    const navigate = useNavigate();

    const {data: invoice} = useQuery(getInvoiceInvoicesInvoiceIdGetOptions({
        path: {invoice_id: parseInt(enforceNonNull(id))}
    }));

    const deleteMutation = useMutation({
        ...deleteInvoiceInvoicesInvoiceIdDeleteMutation(),
        onSuccess: async () => {
            showToast({ severity: 'success', summary: 'Fertig!', detail: 'Rechnung wurde gelöscht.', life: 3000});
            await queryClient.invalidateQueries({
                queryKey: getInvoicesInvoicesGetQueryKey()
            })
            navigate(ROUTES.INVOICES);
        },
        onError: (error) => {
            showToast({ severity: 'error', summary: 'Error!', detail: `Rechnung konnte nicht gelöscht werden. ${error.detail}`, life: 3000});
        }
    });


    if (!id) {
        return <span>Rechnung konnte nicht geladen werden!</span>
    }

    if (!invoice) {
        return <span>Rechnung konnte nicht geladen werden!</span>
    }

    const accept = async () => {
        await deleteMutation.mutateAsync({
            path: {invoice_id: invoice.invoice_id}
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

    const canBeEdited = !["DRAFT", "SAVED"].includes(invoice.status);

    return (
        <>
            <ConfirmDialog/>
            <StepOverviewContent
                header={<h1 className="text-4xl font-bold">Rechnung {invoice.invoice_number}</h1>}
                invoice={invoice}
                footer={
                    <div className="flex justify-content-between mt-2 gap-2">
                        <div className="flex gap-2">
                            <Button
                                label="Löschen"
                                icon="pi pi-trash"
                                className="p-button-danger p-button-rounded"
                                disabled={canBeEdited}
                                onClick={confirm}/>
                            <Button
                                label="Bearbeiten"
                                icon="pi pi-pencil"
                                disabled={canBeEdited}
                                className="p-button-text p-button-rounded"
                                onClick={() => navigate(generatePath(ROUTES.INVOICE_EDIT, { id: invoice.invoice_id.toString() }))}
                            />
                        </div>
                        <Button
                            label="PDF anzeigen"
                            icon="pi pi-file-pdf"
                            className="p-button-rounded"
                            onClick={() => navigate(generatePath(ROUTES.INVOICE_PREVIEW, { id: invoice.invoice_id.toString() }))}
                        />
                    </div>
                }
            />
        </>
    );
}