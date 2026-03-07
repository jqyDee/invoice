import React from 'react';
import { Controller, useForm } from 'react-hook-form';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { InputNumber } from "primereact/inputnumber";
import { InputSwitch } from "primereact/inputswitch";
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
    createDefaultInvoiceItemInvoiceItemsDefaultsPostMutation, getDefaultInvoiceItemsInvoiceItemsDefaultsGetQueryKey
} from '../../api/@tanstack/react-query.gen';
import {
    InvoiceType,
    DefaultInvoiceItemPosition,
    type DefaultInvoiceItemCreate
} from '../../api';
import { useGlobalToast } from "../../hooks/use-global-toast.ts";

interface DefaultItemFormProps {
    onSuccess?: () => void;
}

export const DefaultItemForm: React.FC<DefaultItemFormProps> = ({ onSuccess }) => {
    const queryClient = useQueryClient();
    const { showToast } = useGlobalToast();

    const { control, handleSubmit, reset, formState: { errors }, watch, trigger } = useForm<DefaultInvoiceItemCreate>({
        defaultValues: {
            description: '',
            amount: 0,
            quantity: null,
            number: '',
            type: InvoiceType.KG,
            position: DefaultInvoiceItemPosition.PREPEND,
            is_active_global: true
        }
    });

    const selectedType = watch('type');

    React.useEffect(() => {
        trigger(['quantity', 'number']).then();
    }, [selectedType, trigger]);

    const getFormErrorMessage = (name: keyof DefaultInvoiceItemCreate) => {
        return errors[name] && <small className="p-error block mt-1">{errors[name]?.message}</small>;
    };

    const createMutation = useMutation({
        ...createDefaultInvoiceItemInvoiceItemsDefaultsPostMutation(),
        onSuccess: () => handleSuccess('Position aktualisiert')
    });

    const handleSuccess = async (message: string) => {
        await queryClient.invalidateQueries({ queryKey: getDefaultInvoiceItemsInvoiceItemsDefaultsGetQueryKey() });
        showToast({ severity: 'success', summary: 'Erfolg', detail: message });
        reset();
        onSuccess?.();
    };

    const onSubmit = (data: DefaultInvoiceItemCreate) => {
        createMutation.mutate({
            body: data
        });
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="grid p-fluid mt-2">
            <div className="col-12">
                <h3 className="mt-0">Allgemein</h3>
            </div>

            <div className="col-12 field">
                <label htmlFor="type" className="font-bold">Rechnungstyp</label>
                <Controller
                    name="type"
                    control={control}
                    rules={{ required: 'Typ ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <Dropdown id={field.name} {...field} options={Object.values(InvoiceType)} />
                            {getFormErrorMessage('type')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="description" className="font-bold">Beschreibung</label>
                <Controller
                    name="description"
                    control={control}
                    rules={{ required: 'Beschreibung ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.description ? 'p-invalid' : ''} />
                            {getFormErrorMessage('description')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="amount" className="font-bold">Betrag (€)</label>
                <Controller
                    name="amount"
                    control={control}
                    rules={{ required: 'Betrag ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputNumber
                                id={field.name}
                                value={field.value}
                                onValueChange={(e) => field.onChange(e.value)}
                                mode="currency"
                                currency="EUR"
                                locale="de-DE"
                            />
                            {getFormErrorMessage('amount')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-10 field">
                <label htmlFor="position" className="font-bold">Einfügeposition</label>
                <Controller
                    name="position"
                    control={control}
                    rules={{ required: 'Position ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <Dropdown id={field.name} {...field} options={Object.values(DefaultInvoiceItemPosition)} />
                            {getFormErrorMessage('position')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-2 field flex flex-column justify-content-center">
                <label htmlFor="is_active_global" className="font-bold mb-2">Global Aktiv</label>
                <Controller
                    name="is_active_global"
                    control={control}
                    render={({ field }) => (
                        <InputSwitch id={field.name} checked={field.value} onChange={(e) => field.onChange(e.value)} />
                    )}
                />
            </div>

            <div className="col-12">
                <h3 className="mt-0">Krankengymnastik</h3>
            </div>

            <div className="col-12 field">
                <label htmlFor="quantity" className="font-bold">Standard-Anzahl</label>
                <Controller
                    name="quantity"
                    control={control}
                    render={({ field }) => (
                        <>
                            <InputNumber
                                id={field.name}
                                value={field.value}
                                onValueChange={(e) => field.onChange(e.value)}
                                className={errors.quantity ? 'p-invalid' : ''}
                                placeholder="Leer lassen für dynamische Anzahl. Eintragen für feststehende Anzahl!"
                            />
                        </>
                    )}
                />
            </div>
            <div className="col-12">
                <h3 className="mt-0">Heilpraktiker</h3>
            </div>

            <div className="col-12 field">
                <label htmlFor="number" className="font-bold">Ziffer</label>
                <Controller
                    name="number"
                    control={control}
                    rules={{
                        required: selectedType === InvoiceType.HP ? 'Ziffer ist für HP erforderlich.' : false
                    }}
                    render={({ field }) => (
                        <>
                            <InputText
                                id={field.name}
                                {...field}
                                value={field.value || ''}
                                className={errors.number ? 'p-invalid' : ''}
                                disabled={selectedType !== InvoiceType.HP}
                            />
                            {getFormErrorMessage('number')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 flex justify-content-end mt-4">
                <Button
                    type="submit"
                    label="Speichern"
                    icon="pi pi-check"
                    className="w-auto p-button-rounded"
                    loading={createMutation.isPending}
                />
            </div>
        </form>
    );
};