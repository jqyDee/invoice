import React from 'react';
import { Controller, useForm } from 'react-hook-form';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Button } from 'primereact/button';
import {type InvoiceItemCreate, InvoiceType} from '../../api';
import {InputTextarea} from "primereact/inputtextarea";

export interface TreatmentFormData extends InvoiceItemCreate {
    date?: string;
}

interface TreatmentFormProps {
    initialData?: Partial<TreatmentFormData> | null;
    onSave: (data: TreatmentFormData) => void;
    type: InvoiceType;
    onCancel: () => void;
}

export const InvoiceTreatmentForm: React.FC<TreatmentFormProps> = ({ initialData, onSave, type, onCancel }) => {
    const { control, handleSubmit, formState: { errors } } = useForm<TreatmentFormData>({
        defaultValues: initialData || {
            description: '',
            amount: 0,
            number: '',
            quantity: 1
        }
    });

    const getFormErrorMessage = (name: keyof TreatmentFormData) => {
        return errors[name] && <small className="p-error block mt-1">{errors[name]?.message}</small>;
    };

    return (
        <form onSubmit={handleSubmit(onSave)} className="grid p-fluid mt-2">
            <div className="col-12 field">
                <label htmlFor="description" className="font-bold">Bezeichnung</label>
                <Controller
                    name="description"
                    control={control}
                    rules={{ required: 'Bezeichnung ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputTextarea
                                id={field.name}
                                {...field}
                                style={{minHeight: '10vw'}}
                                className={errors.description ? 'p-invalid' : ''}
                                autoFocus
                            />
                            {getFormErrorMessage('description')}
                        </>
                    )}
                />
            </div>

            {/* Betrag */}
            <div className="col-12 field">
                <label htmlFor="amount" className="font-bold">Betrag (€)</label>
                <Controller
                    name="amount"
                    control={control}
                    rules={{
                        required: 'Betrag ist erforderlich.',
                        min: { value: 0.01, message: 'Betrag muss größer als 0 sein.' }
                    }}
                    render={({ field }) => (
                        <>
                            <InputNumber
                                id={field.name}
                                value={field.value}
                                onValueChange={(e) => field.onChange(e.value ?? 0)}
                                mode="currency"
                                currency="EUR"
                                locale="de-DE"
                                className={errors.amount ? 'p-invalid' : ''}
                            />
                            {getFormErrorMessage('amount')}
                        </>
                    )}
                />
            </div>

            {type !== InvoiceType.KG && (
                <>
                    <div className="col-12 md:col-6 field">
                        <label htmlFor="ziffer" className="font-bold">Ziffer</label>
                        <Controller
                            name="number"
                            control={control}
                            rules={{ required: 'Ziffer ist erforderlich.' }}
                            render={({ field }) => (
                                <>
                                    <InputText
                                        id={field.name}
                                        {...field}
                                        value={field.value || ''}
                                        placeholder="z.B. GÖÄ 1"
                                        className={errors.number ? 'p-invalid' : ''}
                                    />
                                    {getFormErrorMessage('number')}
                                </>
                            )}
                        />
                    </div>

                    <div className="col-12 md:col-6 field">
                        <label htmlFor="date" className="font-bold">Behandlungsatum</label>
                        <Controller
                            name="date"
                            control={control}
                            rules={{ required: 'Datum ist erforderlich.' }}
                            render={({ field }) => (
                                <>
                                    <InputText
                                        id={field.name}
                                        type="date"
                                        {...field}
                                        className={errors.date ? 'p-invalid' : ''}
                                    />
                                    {getFormErrorMessage('date')}
                                </>
                            )}
                        />
                    </div>
                </>
            )}

            {/* Aktions-Buttons */}
            <div className="col-12 flex justify-content-end mt-4 gap-2">
                <Button
                    type="button"
                    label="Abbrechen"
                    icon="pi pi-times"
                    onClick={onCancel}
                    className="p-button-text p-button-rounded w-auto"
                />
                <Button
                    type="submit"
                    label="Speichern"
                    icon="pi pi-check"
                    className="p-button-rounded w-auto"
                />
            </div>
        </form>
    );
};