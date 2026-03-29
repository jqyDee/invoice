import React from "react";
import {Stepper} from "primereact/stepper";
import {StepperPanel} from "primereact/stepperpanel";
import {Button} from "primereact/button";
import {StepGeneralContent} from "./invoice-edit/step-general-content.tsx";
import {StepItemsContent} from "./invoice-edit/step-items-content.tsx";
import {StepOverviewContent} from "./invoice-edit/step-overview-content.tsx";
import {StepDetailsContent} from "./invoice-edit/step-details-content.tsx";
import {UnsavedChangesDialog} from "./invoice-edit/unsaved-changes-dialog.tsx";
import {Header} from "../utilities/header.tsx";
import {useInvoiceEdit} from "../hooks/invoice/use-invoice-edit.ts";


export const InvoiceEditView: React.FC = () => {
    const {
        id,
        invoice,
        updateInvoice,
        isLoading,
        stepperRef,
        goNext,
        goPrev,
        handleSave,
        blocker,
        showLeaveDialog,
        handleSaveDraft,
    } = useInvoiceEdit();

    if (isLoading) return <div>Laden...</div>;

    return (
        <div className="card">
            <Header title={`Rechnung ${id ? "aktualisieren" : "erstellen"}`}/>
            <Stepper ref={stepperRef} linear={!id} headerPosition="bottom" className="mt-4">
                <StepperPanel header="Basisdaten">
                    <StepGeneralContent
                        invoice={invoice}
                        onChange={updateInvoice}
                        next={goNext}
                    />
                </StepperPanel>

                <StepperPanel header="Daten">
                    <StepItemsContent
                        invoice={invoice}
                        onChange={updateInvoice}
                        prev={goPrev}
                        next={goNext}
                    />
                </StepperPanel>

                <StepperPanel header="Details">
                    <StepDetailsContent
                        invoice={invoice}
                        onChange={updateInvoice}
                        prev={goPrev}
                        next={goNext}
                    />
                </StepperPanel>

                <StepperPanel header="Überblick">
                    <StepOverviewContent
                        header={<Header title="Zusammenfassung Ihrer Eingaben"/>}
                        invoice={invoice}
                        footer={
                            <div className="flex justify-content-between mt-2">
                                <Button
                                    label="Zurück"
                                    icon="pi pi-arrow-left"
                                    className="p-button-text"
                                    onClick={goPrev}
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

            <UnsavedChangesDialog
                visible={showLeaveDialog}
                onHide={() => blocker.reset?.()}
                onLeave={() => blocker.proceed?.()}
                onSaveDraft={handleSaveDraft}
            />
        </div>
    );
};
