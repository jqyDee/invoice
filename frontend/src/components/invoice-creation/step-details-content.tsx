import React from "react";
import {Button} from "primereact/button";
import {InputText} from "primereact/inputtext";
import {Header} from "../header.tsx";
import {InputTextarea} from "primereact/inputtextarea";
import {InvoiceType} from "../../api";

interface StepDetailsProps {
    type: InvoiceType;
    invoiceDate: string;
    diagnosis: string;
    prev: (invoiceDate: string, diagnosis: string) => void;
    next: (invoiceDate: string, diagnosis: string) => void;
}

export const StepDetailsContent: React.FC<StepDetailsProps> = ({ type, invoiceDate: initialInvoiceDate, diagnosis: initialDiagnosis, prev, next }) => {
    const [invoiceDate, setInvoiceDate] = React.useState<string>(initialInvoiceDate);
    const [diagnosis, setDiagnosis] = React.useState<string>(initialDiagnosis);

    return (
        <>
            <div className="flex">
                <div className="col-6 flex flex-column">
                    <Header title="Rechnungsdatum"/>
                    <InputText
                        id="invoiceDate"
                        value={invoiceDate}
                        onChange={(e) => setInvoiceDate(e.target.value)}
                        type="date"
                    />
                </div>
                { (type === InvoiceType.HP) &&
                    <div className="col-6 flex flex-column">
                        <Header title="Diagnose"/>
                        <InputTextarea
                            id="invoiceDate"
                            value={diagnosis}
                            autoResize
                            onChange={(e) => setDiagnosis(e.target.value)}
                        />
                    </div>
                }
            </div>

            <div className="flex justify-content-between mt-3">
                <Button label="Zurück" icon="pi pi-arrow-left" className="p-button-text" onClick={() => prev(invoiceDate, diagnosis)} />
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={!invoiceDate || (type === InvoiceType.HP && !diagnosis)}
                    onClick={() => next(invoiceDate, diagnosis)}
                />
            </div>
        </>
    )
}