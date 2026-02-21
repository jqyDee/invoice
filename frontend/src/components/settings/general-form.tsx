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
        onError: () => {
            showToast({ severity: 'error', summary: 'Fehler', detail: 'Einstellungen konnte nicht gespeichert werden. Bitte überprüfe deine Eingabe!', life: 3000 });
        }
    });

    const onSubmit = (data: SettingsUpdate) => {
        updateMutation.mutate({ body: data });
    };

    if (isLoading) return <div>Laden...</div>;

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="grid p-fluid mt-2">
            {/* IBAN: DE + 20 digits for Germany */}
            <div className="col-12 field">
                <label htmlFor="iban" className="font-bold">IBAN (DE)</label>
                <Controller
                    name="iban"
                    control={control}
                    rules={{ required: 'IBAN ist erforderlich.' }}
                    render={({ field }) => (
                        <InputMask
                            id={field.name}
                            value={field.value}
                            onChange={(e) => field.onChange(e.value)}
                            mask="aa99 9999 9999 9999 9999 99" // Standard German format
                            placeholder="DE00 0000 0000 0000 0000 00"
                            className={errors.iban ? 'p-invalid' : ''}
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
                    rules={{ required: 'BIC ist erforderlich.' }}
                    render={({ field }) => (
                        <InputMask
                            id={field.name}
                            value={field.value}
                            onChange={(e) => field.onChange(e.value)}
                            mask="aaaaaaaa?aaa" // 8 chars required, 3 optional
                            placeholder="XXXXXXXX"
                            className={errors.bic ? 'p-invalid' : ''}
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
                            mask="99 999 999 999" // Format: 12 345 678 901
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