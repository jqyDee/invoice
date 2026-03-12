import React from 'react';
import { Controller, useForm } from 'react-hook-form';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { InputNumber } from 'primereact/inputnumber';
import { Button } from 'primereact/button';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getTherapyClausesTherapyClausesGetQueryKey,
    patchTherapyClauseTherapyClausesClauseIdPatchMutation,
    postTherapyClauseTherapyClausesPostMutation,
} from '../../api/@tanstack/react-query.gen';
import { type TherapyClause, type TherapyClauseCreate } from '../../api';
import { useGlobalToast } from '../../hooks/use-global-toast.ts';

interface TherapyClauseFormProps {
    existing?: TherapyClause;
    onSuccess?: () => void;
}

export const TherapyClauseForm: React.FC<TherapyClauseFormProps> = ({ existing, onSuccess }) => {
    const queryClient = useQueryClient();
    const { showToast } = useGlobalToast();

    const { control, handleSubmit, reset, formState: { errors } } = useForm<TherapyClauseCreate>({
        defaultValues: {
            number: existing?.number ?? 1,
            title: existing?.title ?? '',
            description: existing?.description ?? '',
        }
    });

    const invalidate = async () => {
        await queryClient.invalidateQueries({ queryKey: getTherapyClausesTherapyClausesGetQueryKey() });
        showToast({ severity: 'success', summary: 'Erfolg', detail: 'Klausel gespeichert' });
        reset();
        onSuccess?.();
    };

    const createMutation = useMutation({
        ...postTherapyClauseTherapyClausesPostMutation(),
        onSuccess: invalidate,
    });

    const updateMutation = useMutation({
        ...patchTherapyClauseTherapyClausesClauseIdPatchMutation(),
        onSuccess: invalidate,
    });

    const onSubmit = (data: TherapyClauseCreate) => {
        if (existing) {
            updateMutation.mutate({ path: { clause_id: existing.clause_id }, body: data });
        } else {
            createMutation.mutate({ body: data });
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
                    rules={{ required: 'Nummer ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputNumber
                                id={field.name}
                                value={field.value}
                                onValueChange={(e) => field.onChange(e.value)}
                                className={errors.number ? 'p-invalid' : ''}
                                min={1}
                            />
                            {errors.number && <small className="p-error">{errors.number.message}</small>}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-10 field">
                <label htmlFor="title" className="font-bold">Titel</label>
                <Controller
                    name="title"
                    control={control}
                    rules={{ required: 'Titel ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.title ? 'p-invalid' : ''} />
                            {errors.title && <small className="p-error">{errors.title.message}</small>}
                        </>
                    )}
                />
            </div>

            <div className="col-12 field">
                <label htmlFor="description" className="font-bold">Beschreibung</label>
                <Controller
                    name="description"
                    control={control}
                    rules={{ required: 'Beschreibung ist erforderlich.' }}
                    render={({ field }) => (
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
