import React, {useState} from "react";
import {useIsMobile} from "../../hooks/use-is-mobile.ts";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import {Button} from "primereact/button";
import {Tag} from "primereact/tag";
import {Dialog} from "primereact/dialog";
import {Calendar} from "primereact/calendar";
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
import {InputText} from "primereact/inputtext";
import {useGlobalToast} from "../../hooks/use-global-toast.ts";

interface InvoiceTableProps {
    invoices: Invoice[] | undefined;
    isLoading: boolean;
    totalRecords: number;
    page: number;
    pageSize: number;
    onPageChange: (page: number, pageSize: number) => void;
    sortField?: string;
    sortOrder?: "asc" | "desc";
    onSort?: (field: string, order: "asc" | "desc") => void;
}

export const InvoiceTable: React.FC<InvoiceTableProps> = ({invoices, isLoading, totalRecords, page, pageSize, onPageChange, sortField, sortOrder, onSort}) => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const isMobile = useIsMobile();

    const [paidDialogInvoiceId, setPaidDialogInvoiceId] = useState<number | null>(null);
    const [paidDate, setPaidDate] = useState<string | null>(null);

    const {showToast} = useGlobalToast();

    const markPaymentDue = useMutation({
        ...setPaymentDueMutation(),
        onSuccess: () => queryClient.invalidateQueries({queryKey: getInvoicesInvoicesGetQueryKey()}),
    });

    const markPaid = useMutation({
        ...setPaidMutation(),
        onSuccess: async () => {
            setPaidDialogInvoiceId(null);
            setPaidDate(null);
            await queryClient.invalidateQueries({queryKey: getInvoicesInvoicesGetQueryKey()});
        },
    });

    const confirm = (invoice: Invoice) => {
        if (!invoice || !invoice.invoice_id) {
            return
        }

        confirmDialog({
            message: 'Nach dem Herausgeben einer Rechnung kann diese nicht mehr bearbeitet werden. Stellen Sie sicher das die Rechnung korrekt ist!',
            header: 'Herausgeben?',
            icon: 'pi pi-info-circle',
            defaultFocus: 'reject',
            acceptClassName: 'p-button-danger',
            rejectLabel: "Nein",
            acceptLabel: "Ja",
            accept: () => {
                markPaymentDue.mutate({path: {invoice_id: invoice.invoice_id}})
            },
            reject: () => {
            }
        })
    }

    return (
        <>
            <ConfirmDialog/>
            <Dialog
                header="Zahlungsdatum"
                visible={paidDialogInvoiceId !== null}
                onHide={() => setPaidDialogInvoiceId(null)}
                style={{minWidth: '30vw'}}
            >
                <div className="flex flex-column gap-3">
                    <Calendar
                        value={paidDate ? new Date(paidDate + 'T00:00:00') : new Date()}
                        onChange={(e) => setPaidDate(toLocalDateString(e.value as Date))}
                        inline
                        className="w-full"
                    />
                    <InputText
                        value={paidDate || ''}
                        onChange={(e) => setPaidDate(e.target.value)}
                        type="date"
                        className="w-full"
                    />

                    <div className="flex justify-content-end gap-2">
                        <Button
                            label="Abbrechen"
                            className="p-button-text"
                            onClick={() => setPaidDialogInvoiceId(null)}
                        />
                        <Button
                            label="Speichern"
                            icon="pi pi-save"
                            disabled={!paidDate}
                            onClick={() => {
                                if (!paidDate) {
                                    showToast({
                                        severity: 'error',
                                        summary: 'Fehler',
                                        detail: 'Etwas hat nicht geklappt. Bitte versuche es erneut!',
                                        life: 3000
                                    });
                                    return;
                                }

                                markPaid.mutate({
                                    path: {invoice_id: paidDialogInvoiceId!},
                                    body: {paid_at: paidDate}
                                })}
                            }
                        />
                    </div>
                </div>
            </Dialog>

            <DataTable
                value={invoices}
                lazy
                paginator
                rows={pageSize}
                first={(page - 1) * pageSize}
                totalRecords={totalRecords}
                onPage={(e) => onPageChange(Math.floor(e.first / e.rows) + 1, e.rows)}
                sortField={sortField}
                sortOrder={sortOrder === "desc" ? -1 : 1}
                onSort={onSort ? (e) => onSort(e.sortField, e.sortOrder === -1 ? "desc" : "asc") : undefined}
                rowsPerPageOptions={[10, 20, 50, 100]}
                removableSort
                key="invoice_id"
                breakpoint="960px"
                emptyMessage="Keine Rechnungen gefunden"
                className="mt-2"
                stripedRows
                size="small"
                showGridlines
                loading={isLoading}
            >
                <Column field="invoice_number" header="Rechnungsnummer" sortable/>
                {!isMobile && (
                    <Column
                        field="invoice_date"
                        header="Rechnungsdatum"
                        sortable
                        body={(e: Invoice) => toGermanDateString(new Date(e.invoice_date))}
                    />
                )}
                {!isMobile && <Column field="type" header="Rechnungstyp" sortable/>}
                {!isMobile && (
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
                )}
                {!isMobile && (
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
                )}
                <Column
                    header="Aktionen"
                    alignHeader="right"
                    className="white-space-nowrap"
                    body={(e: Invoice) => (
                        <div className="flex flex-column md:flex-row gap-2 justify-content-end align-items-end">
                            <div className="flex gap-2">
                                <Button
                                    onClick={() => navigate(generatePath(ROUTES.INVOICE_PREVIEW, {id: e.invoice_id.toString()}))}
                                    icon="pi pi-file-pdf"
                                    tooltip="PDF anzeigen"
                                    tooltipOptions={{showDelay: 1000}}
                                    className="p-button-rounded"
                                />
                                <Button
                                    icon="pi pi-info-circle"
                                    className="p-button-rounded"
                                    tooltip="Rechnungs details anzeigen"
                                    tooltipOptions={{showDelay: 1000}}
                                    onClick={() => navigate(generatePath(ROUTES.INVOICE, {id: e.invoice_id.toString()}))}
                                />
                            </div>
                            <div className="flex gap-2">
                                <Button
                                    icon="pi pi-send"
                                    className="p-button-rounded"
                                    tooltip="Herausgeben"
                                    tooltipOptions={{showDelay: 1000}}
                                    disabled={e.status !== InvoiceStatus.SAVED || markPaymentDue.isPending}
                                    onClick={() => confirm(e)}
                                />
                                <Button
                                    icon="pi pi-check-circle"
                                    className="p-button-rounded"
                                    tooltip="Als bezahlt markieren"
                                    tooltipOptions={{showDelay: 1000}}
                                    disabled={e.status !== InvoiceStatus.PAYMENT_DUE}
                                    onClick={() => {
                                        setPaidDialogInvoiceId(e.invoice_id);
                                        setPaidDate(null);
                                    }}
                                />
                            </div>
                        </div>
                    )}
                />
            </DataTable>
        </>
    );
};
