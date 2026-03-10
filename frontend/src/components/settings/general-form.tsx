import React, { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { Button } from 'primereact/button';
import { InputNumber } from "primereact/inputnumber";
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import {
    getSettingsSettingsGetOptions,
    updateSettingsSettingsPatchMutation
} from '../../api/@tanstack/react-query.gen';
import { type SettingsUpdate } from '../../api';
import {InputMask} from "primereact/inputmask";
import {useGlobalToast} from "../../hooks/use-global-toast.ts";

export const GeneralForm: React.FC = () => {
    const queryClient = useQueryClient();
    const { showToast } = useGlobalToast();

    const { data: settings, isLoading } = useQuery({
        ...getSettingsSettingsGetOptions(),
        retry: false,
    });

    const { control, handleSubmit, reset, formState: { errors } } = useForm<SettingsUpdate>({
        defaultValues: {
            iban: '',
            bic: '',
            tax_id: '',
            price_from: 0,
            price_to: 0
        }
    });

    useEffect(() => {
        if (settings) {
            reset(settings);
        } else {
            // Ensure form is empty/default if no settings exist yet
            reset({
                iban: '',
                bic: '',
                tax_id: '',
                price_from: 0,
                price_to: 0
            });
        }
    }, [settings, reset]);

    const updateMutation = useMutation({
        ...updateSettingsSettingsPatchMutation(),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: getSettingsSettingsGetOptions().queryKey });
            showToast({ severity: 'success', summary: 'Erfolg', detail: 'Einstellungen gespeichert.', life: 3000 });
        },
        onError: (error) => {
            showToast({ severity: 'error', summary: 'Fehler', detail: `Einstellungen konnte nicht gespeichert werden. ${JSON.stringify(error.detail)}`, life: 3000 });
        }
    });

    const onSubmit = (data: SettingsUpdate) => {
        data.iban = data.iban.toUpperCase();
        console.log(data)
        updateMutation.mutate({ body: data });
    };

    if (isLoading) return <div>Laden...</div>;

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="grid p-fluid mt-2">
            {/* IBAN: DE + 20 digits for Germany */}
            <div className="col-12 field">
                <label htmlFor="iban" className="font-bold">IBAN</label>
                <Controller
                    name="iban"
                    control={control}
                    rules={{
                        required: 'IBAN ist erforderlich.',
                        pattern: {
                            value: /^[a-zA-Z]{2}\d{20}$/,
                            message: 'Format: DE99 9999 9999 9999 9999 99!'
                        },
                    }}
                    render={({ field }) => (
                        <InputMask
                            id={field.name}
                            value={field.value}
                            mask="aa99 9999 9999 9999 9999 99" // Standard German format
                            placeholder="DE00 0000 0000 0000 0000 00"
                            unmask={true}
                            className={errors.iban ? 'p-invalid' : ''}
                            style={{ textTransform: 'uppercase' }}
                            onChange={(e) => {
                                const cleanedValue = e.value
                                    ? e.value.replace(/[^a-zA-Z0-9]/g, '')
                                    : '';

                                field.onChange(cleanedValue);
                            }}
                        />
                    )}
                />
                {errors.iban && <small className="p-error">{errors.iban.message}</small>}
            </div>

            {/* BIC: 8 or 11 characters */}
            <div className="col-12 md:col-6 field">
                <label htmlFor="bic" className="font-bold">BIC</label>
                <Controller
                    name="bic"
                    control={control}
                    rules={{
                        required: 'BIC ist erforderlich.',
                        pattern: {
                            value: /^[a-zA-Z]{6}[a-zA-Z0-9]{2}([a-zA-Z0-9]{3})?$/,
                            message: 'Format: 8 oder 11 Zeichen (z.B. AAAAAA11 oder AAAAAA11XXX)'
                        },
                    }}
                    render={({ field }) => (
                        <InputMask
                            id={field.name}
                            value={field.value}
                            mask="aaaaaa**?***"
                            placeholder="XXXXXXXX"
                            unmask={true}
                            style={{ textTransform: 'uppercase' }}
                            className={errors.bic ? 'p-invalid' : ''}
                            onChange={(e) => {
                                const cleanValue = e.value ? e.value.replace(/[^a-zA-Z0-9]/g, '') : '';
                                field.onChange(cleanValue);
                            }}
                        />
                    )}
                />
                {errors.bic && <small className="p-error">{errors.bic.message}</small>}
            </div>

            {/* Tax ID: 11 digits for personal Steuer-ID */}
            <div className="col-12 md:col-6 field">
                <label htmlFor="tax_id" className="font-bold">Steuer-ID</label>
                <Controller
                    name="tax_id"
                    control={control}
                    rules={{ required: 'Steuer-ID ist erforderlich.' }}
                    render={({ field }) => (
                        <InputMask
                            id={field.name}
                            value={field.value}
                            onChange={(e) => field.onChange(e.value)}
                            mask="999/999/99999" // Format: 12 345 678 901
                            unmask={true}
                            placeholder="00 000 000 000"
                            className={errors.tax_id ? 'p-invalid' : ''}
                        />
                    )}
                />
                {errors.tax_id && <small className="p-error">{errors.tax_id.message}</small>}
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="price_from" className="font-bold">Preis Von (€)</label>
                <Controller
                    name="price_from"
                    control={control}
                    render={({ field }) => (
                        <InputNumber
                            id={field.name}
                            value={field.value}
                            onValueChange={(e) => field.onChange(e.value ?? 0)}
                            mode="currency"
                            currency="EUR"
                            locale="de-DE"
                        />
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="price_to" className="font-bold">Preis Bis (€)</label>
                <Controller
                    name="price_to"
                    control={control}
                    render={({ field }) => (
                        <InputNumber
                            id={field.name}
                            value={field.value}
                            onValueChange={(e) => field.onChange(e.value ?? 0)}
                            mode="currency"
                            currency="EUR"
                            locale="de-DE"
                        />
                    )}
                />
            </div>

            <div className="col-12 flex justify-content-end mt-2">
                <Button
                    type="submit"
                    label="Einstellungen Speichern"
                    icon="pi pi-save"
                    className="w-auto p-button-rounded"
                    loading={updateMutation.isPending}
                />
            </div>
        </form>
    );
};