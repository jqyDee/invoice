import React from "react";
import {Button} from "primereact/button";
import {InputText} from "primereact/inputtext";
import {Header} from "../../utilities/header.tsx";
import {InputTextarea} from "primereact/inputtextarea";
import {type InvoiceCreate, InvoiceType, type InvoiceUpdate} from "../../api";

interface StepDetailsProps {
    invoice: InvoiceCreate | InvoiceUpdate;
    onChange: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
    prev: () => void;
    next: () => void;
}

export const StepDetailsContent: React.FC<StepDetailsProps> = ({ invoice, onChange, prev, next }) => {
    return (
        <>
            <div className="flex flex-column md:flex-row">
                <div className="flex flex-column">
                    <Header title="Rechnungsdatum"/>
                    <InputText
                        id="invoiceDate"
                        value={invoice.invoice_date}
                        onChange={(e) => onChange({ invoice_date: e.target.value })}
                        type="date"
                    />
                </div>
                { (invoice.type === InvoiceType.HP) &&
                    <div className="flex flex-column">
                        <Header title="Diagnose"/>
                        <InputTextarea
                            id="invoiceDate"
                            value={invoice.diagnosis || ""}
                            autoResize
                            onChange={(e) => onChange({ diagnosis: e.target.value })}
                        />
                    </div>
                }
            </div>

            <div className="flex justify-content-between mt-3">
                <Button
                    label="Zurück"
                    icon="pi pi-arrow-left"
                    className="p-button-text"
                    onClick={prev}
                />
                <Button
                    label="Weiter"
                    icon="pi pi-arrow-right"
                    iconPos="right"
                    disabled={!invoice.invoice_date || (invoice.type === InvoiceType.HP && !invoice.diagnosis)}
                    onClick={next}
                />
            </div>
        </>
    )
}