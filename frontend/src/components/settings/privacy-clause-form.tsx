import React from 'react';
import {Controller, useForm} from 'react-hook-form';
import {InputText} from 'primereact/inputtext';
import {InputTextarea} from 'primereact/inputtextarea';
import {InputNumber} from 'primereact/inputnumber';
import {InputSwitch} from 'primereact/inputswitch';
import {Button} from 'primereact/button';
import {useMutation, useQueryClient} from '@tanstack/react-query';
import {
    getPrivacyClausesPrivacyClausesGetQueryKey,
    patchPrivacyClausePrivacyClausesClauseIdPatchMutation,
    postPrivacyClausePrivacyClausesPostMutation,
} from '../../api/@tanstack/react-query.gen';
import {type PrivacyClause, type PrivacyClauseCreate} from '../../api';
import {useGlobalToast} from '../../hooks/use-global-toast.ts';

interface PrivacyClauseFormProps {
    existing?: PrivacyClause;
    onSuccess?: () => void;
}

export const PrivacyClauseForm: React.FC<PrivacyClauseFormProps> = ({existing, onSuccess}) => {
    const queryClient = useQueryClient();
    const {showToast} = useGlobalToast();

    const {control, handleSubmit, reset, watch, formState: {errors}} = useForm<PrivacyClauseCreate>({
        defaultValues: {
            number: existing?.number ?? 1,
            title: existing?.title ?? '',
            description: existing?.description ?? '',
            is_preamble: existing?.is_preamble ?? false,
        }
    });

    const isPreamble = watch('is_preamble');

    const invalidate = async () => {
        await queryClient.invalidateQueries({queryKey: getPrivacyClausesPrivacyClausesGetQueryKey()});
        showToast({severity: 'success', summary: 'Erfolg', detail: 'Klausel gespeichert'});
        reset();
        onSuccess?.();
    };

    const createMutation = useMutation({
        ...postPrivacyClausePrivacyClausesPostMutation(),
        onSuccess: invalidate,
    });

    const updateMutation = useMutation({
        ...patchPrivacyClausePrivacyClausesClauseIdPatchMutation(),
        onSuccess: invalidate,
    });

    const onSubmit = (data: PrivacyClauseCreate) => {
        if (existing) {
            updateMutation.mutate({path: {clause_id: existing.clause_id}, body: data});
        } else {
            createMutation.mutate({body: data});
        }
    };

    const isPending = createMutation.isPending || updateMutation.isPending;

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="grid p-fluid mt-2">
            <div className="col-12 md:col-2 field">
                <label htmlFor="number" className="font-bold">Nummer</label>
                <Controller
                    name="number"
                    control={control}
                    rules={{required: 'Nummer ist erforderlich.'}}
                    render={({field}) => (
                        <>
                            <InputNumber
                                id={field.name}
                                value={field.value}
                                onValueChange={(e) => field.onChange(e.value)}
                                className={errors.number ? 'p-invalid' : ''}
                                min={0}
                            />
                            {errors.number && <small className="p-error">{errors.number.message}</small>}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-8 field">
                <label htmlFor="title" className="font-bold">Titel</label>
                <Controller
                    name="title"
                    control={control}
                    render={({field}) => (
                        <InputText
                            id={field.name}
                            {...field}
                            disabled={isPreamble}
                            className={errors.title ? 'p-invalid' : ''}
                        />
                    )}
                />
            </div>

            <div className="col-12 md:col-2 field flex flex-column align-items-start">
                <label className="font-bold mb-2">Präambel</label>
                <Controller
                    name="is_preamble"
                    control={control}
                    render={({field}) => (
                        <InputSwitch
                            checked={field.value}
                            onChange={(e) => field.onChange(e.value)}
                        />
                    )}
                />
            </div>

            <div className="col-12 field">
                <label htmlFor="description" className="font-bold">Beschreibung</label>
                <Controller
                    name="description"
                    control={control}
                    rules={{required: 'Beschreibung ist erforderlich.'}}
                    render={({field}) => (
                        <>
                            <InputTextarea
                                id={field.name}
                                {...field}
                                rows={5}
                                className={errors.description ? 'p-invalid' : ''}
                            />
                            {errors.description && <small className="p-error">{errors.description.message}</small>}
                        </>
                    )}
                />
            </div>

            <div className="col-12 flex justify-content-end mt-2">
                <Button
                    type="submit"
                    label="Speichern"
                    icon="pi pi-save"
                    className="w-auto p-button-rounded"
                    loading={isPending}
                />
            </div>
        </form>
    );
};
