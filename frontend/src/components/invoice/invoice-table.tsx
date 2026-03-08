import React, {useState} from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import { Tag } from "primereact/tag";
import { Dialog } from "primereact/dialog";
import { Calendar } from "primereact/calendar";
import {type Invoice, InvoiceStatus} from "../../api";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../../config/routes.ts";
import {toGermanStatus, toSeverityStatus} from "../../utilities/status.ts";
import {useMutation, useQueryClient} from "@tanstack/react-query";
import {
    getInvoicesInvoicesGetQueryKey,
    setPaymentDueMutation,
    setPaidMutation
} from "../../api/@tanstack/react-query.gen.ts";
import {toGermanDateString, toLocalDateString} from "../../utilities/local-date-string.ts";
import {ConfirmDialog, confirmDialog} from "primereact/confirmdialog";

interface InvoiceTableProps {
    invoices: Invoice[] | undefined;
    isLoading: boolean;
}

export const InvoiceTable: React.FC<InvoiceTableProps> = ({ invoices, isLoading }) => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [paidDialogInvoiceId, setPaidDialogInvoiceId] = useState<number | null>(null);
    const [paidDate, setPaidDate] = useState<Date | null>(null);

    const markPaymentDue = useMutation({
        ...setPaymentDueMutation(),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: getInvoicesInvoicesGetQueryKey() }),
    });

    const markPaid = useMutation({
        ...setPaidMutation(),
        onSuccess: async () => {
            setPaidDialogInvoiceId(null);
            setPaidDate(null);
            await queryClient.invalidateQueries({ queryKey: getInvoicesInvoicesGetQueryKey() });
        },
    });

    const confirm = (invoice: Invoice) => {
        if (!invoice || !invoice.invoice_id) {
            return
        }

        confirmDialog({
            message: 'Das Herausgeben einer Rechnung kann nicht rückgängig gemacht werden. Bitte stellen Sie die Korrekheit der Rechnung sicher vor dem Herausgeben.',
            header: 'Herausgeben?',
            icon: 'pi pi-info-circle',
            defaultFocus: 'reject',
            acceptClassName: 'p-button-danger',
            rejectLabel: "Nein",
            acceptLabel: "Ja",
            accept: () => {
                markPaymentDue.mutate({ path: { invoice_id: invoice.invoice_id } })
            },
            reject: () => {}
        })
    }

    return (
        <>
            <ConfirmDialog />
            <Dialog
                header="Zahlungsdatum"
                visible={paidDialogInvoiceId !== null}
                onHide={() => setPaidDialogInvoiceId(null)}
                style={{ minWidth: '30vw' }}
            >
                <div className="flex flex-column gap-3">
                    <Calendar value={paidDate} onChange={(e) => setPaidDate(e.value as Date)} inline />
                    <div className="flex justify-content-end gap-2">
                        <Button
                            label="Abbrechen"
                            className="p-button-text"
                            onClick={() => setPaidDialogInvoiceId(null)}
                        />
                        <Button
                            label="Speichern"
                            disabled={!paidDate}
                            onClick={() => markPaid.mutate({
                                path: { invoice_id: paidDialogInvoiceId! },
                                body: { paid_at: toLocalDateString(paidDate!) }
                            })}
                        />
                    </div>
                </div>
            </Dialog>

            <DataTable
                value={invoices}
                paginator
                rows={10}
                key="invoice_id"
                breakpoint="960px"
                emptyMessage="Keine Rechnungen gefunden"
                className="mt-2"
                stripedRows
                size="small"
                removableSort
                showGridlines
                loading={isLoading}
                sortField="updated_at"
                sortOrder={-1}
            >
                <Column field="invoice_number" header="Rechnungsnummer" sortable />
                <Column
                    field="invoice_date"
                    header="Rechnungsdatum"
                    sortable
                    body={(e: Invoice) => toGermanDateString(new Date(e.invoice_date))}
                />
                <Column field="type" header="Rechnungstyp" sortable />
                <Column field="updated_at"
                        header="Änderungsdatum"
                        sortable
                        body={(e: Invoice) => new Date(e.updated_at).toLocaleString('de-DE', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                />
                <Column
                    field="status"
                    header="Status"
                    sortable
                    body={(e: Invoice) => (
                        <Tag
                            severity={toSeverityStatus(e.status)}
                            value={toGermanStatus(e.status)}
                            rounded
                        />
                    )}
                />
                <Column
                    header="Aktionen"
                    alignHeader="right"
                    body={(e: Invoice) => (
                        <div className="flex gap-2 justify-content-end">
                            <Button
                                onClick={() => navigate(generatePath(ROUTES.INVOICE_PREVIEW, { id: e.invoice_id.toString() }))}
                                icon="pi pi-file-pdf"
                                tooltip="PDF anzeigen"
                                tooltipOptions={{ showDelay: 1000 }}
                                className="p-button-rounded"
                            />
                            <Button
                                icon="pi pi-info-circle"
                                className="p-button-rounded"
                                tooltip="Rechnungs details anzeigen"
                                tooltipOptions={{ showDelay: 1000 }}
                                onClick={() => navigate(generatePath(ROUTES.INVOICE, { id: e.invoice_id.toString() }))}
                            />
                            <Button
                                icon="pi pi-send"
                                className="p-button-rounded"
                                tooltip="Herausgeben"
                                tooltipOptions={{ showDelay: 1000 }}
                                disabled={e.status !== InvoiceStatus.SAVED || markPaymentDue.isPending}
                                onClick={() => confirm(e)}
                            />
                            <Button
                                icon="pi pi-check-circle"
                                className="p-button-rounded"
                                tooltip="Als bezahlt markieren"
                                tooltipOptions={{ showDelay: 1000 }}
                                disabled={e.status !== InvoiceStatus.PAYMENT_DUE}
                                onClick={() => { setPaidDialogInvoiceId(e.invoice_id); setPaidDate(null); }}
                            />
                        </div>
                    )}
                />
            </DataTable>
        </>
    );
};
