import {Stepper} from "primereact/stepper";
import {StepperPanel} from "primereact/stepperpanel";
import {StepGeneralContent} from "./invoice-creation/step-general-content.tsx";
import {StepItemsContent} from "./invoice-creation/step-items-content.tsx";
import React, {useRef} from "react";
import {StepOverviewContent} from "./invoice-creation/step-overview-content.tsx";
import {StepDetailsContent} from "./invoice-creation/step-details-content.tsx";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {
    createInvoiceInvoicesPostMutation,
    getInvoicesInvoicesGetQueryKey,
    getInvoiceInvoicesInvoiceIdGetOptions,
    updateInvoiceInvoicesInvoiceIdPatchMutation,
    getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions,
    getInvoiceInvoicesInvoiceIdGetQueryKey
} from "../api/@tanstack/react-query.gen.ts";
import {Header} from "../utilities/header.tsx";
import {Button} from "primereact/button";
import {generatePath, useNavigate, useParams} from "react-router-dom";
import {ROUTES} from "../config/routes.ts";
import {toLocalDateString} from "../utilities/local-date-string.ts";
import {useGlobalToast} from "../hooks/use-global-toast.ts";
import {type InvoiceCreate, InvoiceType, type InvoiceUpdate} from "../api";


export const InvoiceCreateView: React.FC = () => {
    const { id } = useParams(); // Optional type
    const stepperRef = useRef<any>(null);
    const navigate = useNavigate();

    const [invoice, setInvoice] = React.useState<InvoiceCreate | InvoiceUpdate>({
        patient_id: 0,
        invoice_date: toLocalDateString(new Date()),
        type: InvoiceType.HP,
        user_items: [],
        default_item_ids: [], // Track IDs for the association table
        dates: [],
        diagnosis: "",
    });

    const {showToast} = useGlobalToast();

    const {data: invoiceToUpdate, isLoading } = useQuery({
        ...getInvoiceInvoicesInvoiceIdGetOptions({
            path: {invoice_id: parseInt(id!)} // this is safe as this can only run if invoiceId is present
        }),
        enabled: !!id,
        retry: false,
    })

    const { data: availableDefaults } = useQuery(getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
        query: { invoice_type: invoice.type }
    }));

    React.useEffect(() => {
        if (id && invoiceToUpdate) {
            // Logic for UPDATE: Use existing associations from the DB
            setInvoice({
                patient_id: invoiceToUpdate.patient_id,
                invoice_date: invoiceToUpdate.invoice_date,
                type: invoiceToUpdate.type,
                user_items: invoiceToUpdate.user_items,
                default_item_ids: invoiceToUpdate.default_items.map(d => d.default_item_id),
                dates: invoiceToUpdate.dates,
                diagnosis: invoiceToUpdate.diagnosis,
            });
        } else if (!id && availableDefaults) {
            // Logic for CREATE: Set globally active defaults by default
            const activeGlobalIds = availableDefaults
                .filter(d => d.is_active_global) // Filter for globally active items
                .map(d => d.default_item_id);

            setInvoice(prev => ({
                ...prev,
                default_item_ids: activeGlobalIds
            }));
        }
    }, [id, invoiceToUpdate, availableDefaults]);

    const updateInvoice = (fields: Partial<InvoiceCreate | InvoiceUpdate>) => {
        setInvoice(prev => ({ ...prev, ...fields }));
    };


    const queryClient = useQueryClient();

    const createMutation = useMutation({
        ...createInvoiceInvoicesPostMutation(),
        onSuccess: () => handleSuccess(false)
    });

    const updateMutation = useMutation({
        ...updateInvoiceInvoicesInvoiceIdPatchMutation(),
        onSuccess: () => handleSuccess(true)
    });

    const handleSuccess = async (isUpdate: boolean) => {
        showToast({
            severity: 'success',
            summary: 'Fertig!',
            detail: `Rechnung wurde ${isUpdate ? 'aktualisiert' : 'gespeichert'}.`,
            life: 3000
        });
        await queryClient.invalidateQueries({ queryKey: getInvoicesInvoicesGetQueryKey() });
    };

    const handleSave = async () => {
        try {
            let result;
            if (id) {
                result = await updateMutation.mutateAsync({
                    path: { invoice_id: parseInt(id) },
                    body: invoice as InvoiceUpdate
                });
            } else {
                result = await createMutation.mutateAsync({
                    body: invoice as InvoiceCreate
                });
            }

            await queryClient.invalidateQueries({
                queryKey: getInvoiceInvoicesInvoiceIdGetQueryKey({
                    path: {invoice_id: result.invoice_id}
                })
            })

            navigate(generatePath(ROUTES.INVOICE, { id: result.invoice_id.toString() }));
        } catch (error) {
            showToast({ severity: 'error', summary: 'Fehler', detail: "Speichern fehlgeschlagen" });
        }
    };

    if (isLoading) return <div>Laden...</div>

    return (
        <div className="card">
            <Header title={`Rechnung ${id ? "aktualisieren" : "erstellen"}`} />
            <Stepper ref={stepperRef} linear={!id} headerPosition="bottom" className="mt-4">
                <StepperPanel header="Basisdaten">
                    <StepGeneralContent
                        invoice={invoice}
                        onChange={updateInvoice}
                        next={() => stepperRef.current.nextCallback()}
                    />
                </StepperPanel>

                <StepperPanel header="Daten">
                    <StepItemsContent
                        invoice={invoice}
                        onChange={updateInvoice}
                        prev={() => stepperRef.current.prevCallback()}
                        next={() => stepperRef.current.nextCallback()}
                    />
                </StepperPanel>

                <StepperPanel header="Details">
                    <StepDetailsContent
                        invoice={invoice}
                        onChange={updateInvoice}
                        prev={() => stepperRef.current.prevCallback()}
                        next={() => stepperRef.current.nextCallback()}
                    />
                </StepperPanel>

                <StepperPanel header="Überblick">
                    <StepOverviewContent
                        header={<Header title="Zusammenfassung Ihrer Eingaben" />}
                        invoice={invoice}
                        footer={
                            <div className="flex justify-content-between mt-2">
                                <Button
                                    label="Zurück"
                                    icon="pi pi-arrow-left"
                                    className="p-button-text"
                                    onClick={() => stepperRef.current.prevCallback()}
                                />
                                <Button
                                    label={`Rechnung ${id ? "aktualisieren" : "erstellen"}`}
                                    icon="pi pi-check"
                                    iconPos="right"
                                    onClick={handleSave}
                                />
                            </div>
                        }
                    />
                </StepperPanel>
            </Stepper>
        </div>
    );
};