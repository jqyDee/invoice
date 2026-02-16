import {Stepper} from "primereact/stepper";
import {StepperPanel} from "primereact/stepperpanel";
import {StepGeneralContent} from "./invoice-creation/step-general-content.tsx";
import {StepItemsContent} from "./invoice-creation/step-items-content.tsx";
import React, {useRef} from "react";
import {
    type InvoiceCreate, type InvoiceDateCreate, type InvoiceItemCreate, InvoiceType,
    type Patient
} from "../api";
import {StepOverviewContent} from "./invoice-creation/step-overview-content.tsx";
import {StepDetailsContent} from "./invoice-creation/step-details-content.tsx";
import {useMutation, useQueryClient} from "@tanstack/react-query";
import {createInvoiceInvoicesPostMutation, getInvoicesInvoicesGetQueryKey} from "../api/@tanstack/react-query.gen.ts";
import {Header} from "./header.tsx";
import {Button} from "primereact/button";
import {useNavigate} from "react-router-dom";
import {ROUTES} from "../config/routes.ts";
import {toLocalDateString} from "../utilities/local-date-string.ts";
import {useGlobalToast} from "../hooks/use-global-toast.ts";


export const InvoiceCreateView: React.FC = () => {
    const stepperRef = useRef<any>(null);
    const navigate = useNavigate();

    const {showToast} = useGlobalToast();

    const [invoiceData, setInvoiceData] = React.useState<Partial<InvoiceCreate>>({
        patient_id: undefined,
        is_draft: true,
        invoice_date: undefined,
        diagnosis: undefined,
        type: undefined,
        dates: [],
        items: []
    });

    const [selectedPatient, setSelectedPatient] = React.useState<Patient>();
    const [selectedType, setSelectedType] = React.useState<InvoiceType>(InvoiceType.HP);
    const [selectedDates, setSelectedDates] = React.useState<InvoiceDateCreate[]>([]);
    const [selectedItems, setSelectedItems] = React.useState<InvoiceItemCreate[]>([]);
    const [selectedInvoiceDate, setSelectedInvoiceDate] = React.useState<string>(() => toLocalDateString(new Date(Date.now())));
    const [selectedDiagnosis, setSelectedDiagnosis] = React.useState<string>("");

    const queryClient = useQueryClient();

    const createMutation = useMutation({
        ...createInvoiceInvoicesPostMutation(),
        onSuccess: async () => {
            showToast({ severity: 'success', summary: 'Fertig!', detail: 'Rechnung wurde gespeichert.', life: 3000});
            await queryClient.invalidateQueries({
                queryKey: getInvoicesInvoicesGetQueryKey()
            });
        }
    });

    const handlePatientSelected = (patient: Patient, invoiceType: InvoiceType) => {
        setSelectedPatient(patient);
        setSelectedType(invoiceType);
        setInvoiceData(prev => ({ ...prev, patient_id: patient.patient_id, type: invoiceType }));
        stepperRef.current.nextCallback();
    };

    const handleItemsDatesSelected = (dates: InvoiceDateCreate[], items: InvoiceItemCreate[]) => {
        setSelectedDates(dates);
        setSelectedItems(items);
        setInvoiceData(prev => ({...prev, dates: dates, items: items}));
    };

    const handleItemsDatesStepForward = (dates: InvoiceDateCreate[], items: InvoiceItemCreate[]) => {
        handleItemsDatesSelected(dates, items);
        stepperRef.current.nextCallback();
    }

    const handleItemsDatesStepBackwards = (dates: InvoiceDateCreate[], items: InvoiceItemCreate[]) => {
        handleItemsDatesSelected(dates, items);
        stepperRef.current.prevCallback();
    }

    const handleDetailsSelected = (invoiceDate: string, diagnosis: string) => {
        setSelectedInvoiceDate(invoiceDate);
        setSelectedDiagnosis(diagnosis);
        setInvoiceData(prev => ({...prev, invoice_date: invoiceDate, diagnosis: diagnosis}))
    }

    const handleDetailsStepForward = (invoiceDate: string, diagnosis: string) => {
        handleDetailsSelected(invoiceDate, diagnosis);
        stepperRef.current.nextCallback();
    }

    const handleDetailsStepBackwards = (invoiceDate: string, diagnosis: string) => {
        handleDetailsSelected(invoiceDate, diagnosis);
        stepperRef.current.prevCallback();
    }

    const handleCreate = async () => {
        if (
            invoiceData.patient_id === undefined ||
            !invoiceData.invoice_date ||
            !invoiceData.type ||
            !invoiceData.items
        ) {
            showToast({ severity: 'error', summary: 'Fehler', detail: 'Daten stimmen nicht. Bitte versuche die Rechnung erneut zu erstellen.' });
            return;
        }

        const payload: InvoiceCreate = {
            patient_id: invoiceData.patient_id,
            invoice_date: invoiceData.invoice_date,
            type: invoiceData.type,
            items: invoiceData.items,
            dates: invoiceData.dates || [],
            diagnosis: invoiceData.diagnosis || null,
            is_draft: invoiceData.is_draft ?? true
        };

        try {
            const createdInvoice = await createMutation.mutateAsync({
                body: payload
            });

            if (createdInvoice && createdInvoice.invoice_id) {
                navigate(ROUTES.INVOICE.replace(':id', createdInvoice.invoice_id.toString()))
            }
        } catch (error) {
            showToast({ severity: 'error', summary: 'Fehler', detail: "Failed to create invoice:" + JSON.stringify(error) });
        }
    };

    return (
        <div className="card">
            <Stepper ref={stepperRef} linear headerPosition="bottom">
                <StepperPanel header="Basisdaten">
                    <StepGeneralContent
                        next={handlePatientSelected}
                        initialPatient={selectedPatient}
                        initialType={selectedType}
                    />
                </StepperPanel>

                <StepperPanel header="Daten">
                    <StepItemsContent
                        type={selectedType}
                        dates={selectedDates}
                        items={selectedItems}
                        prev={handleItemsDatesStepBackwards}
                        next={handleItemsDatesStepForward}
                    />
                </StepperPanel>

                <StepperPanel header="Details">
                    <StepDetailsContent
                        type={selectedType}
                        invoiceDate={selectedInvoiceDate}
                        diagnosis={selectedDiagnosis}
                        prev={handleDetailsStepBackwards}
                        next={handleDetailsStepForward}
                    />
                </StepperPanel>

                <StepperPanel header="Überblick">
                    <StepOverviewContent
                        header={<Header title="Zusammenfassung Ihrer Eingaben" />}
                        type={selectedType}
                        invoiceDate={selectedInvoiceDate}
                        patient={selectedPatient!}
                        items={selectedItems}
                        dates={selectedDates.map(d => new Date(d.date))}
                        diagnosis={selectedDiagnosis}
                        isPreview={true}
                        footer={
                            <div className="flex justify-content-between mt-2">
                                <Button
                                    label="Zurück"
                                    icon="pi pi-arrow-left"
                                    className="p-button-text"
                                    onClick={() => stepperRef.current.prevCallback()}
                                />
                                <Button
                                    label="Rechnung erstellen"
                                    icon="pi pi-check"
                                    iconPos="right"
                                    onClick={handleCreate}
                                />
                            </div>
                        }
                    />
                </StepperPanel>
            </Stepper>
        </div>
    );
};