import React from 'react';
import {Controller, useForm} from 'react-hook-form';
import {InputText} from 'primereact/inputtext';
import {Dropdown} from 'primereact/dropdown';
import {Button} from 'primereact/button';
import {InputNumber} from "primereact/inputnumber";
import {type QueryObserverResult, type RefetchOptions, useMutation, useQueryClient} from '@tanstack/react-query';
import {
    createPatientPatientsPostMutation,
    deletePatientPatientsPatientIdDeleteMutation,
    getPatientsPatientsGetOptions,
    updatePatientPatientsPatientIdPutMutation,
} from '../api/@tanstack/react-query.gen';
import {Gender, type HttpValidationError, type Patient, type PatientCreate} from '../api';
import {confirmDialog, ConfirmDialog} from "primereact/confirmdialog";
import {useGlobalToast} from "../hooks/use-global-toast.ts";

interface PatientFormProps {
    onSuccess?: () => void;
    patientToEdit?: Patient | null;
    refetch: (options?: RefetchOptions) => Promise<QueryObserverResult<Patient[], HttpValidationError>>;
}

export const PatientForm: React.FC<PatientFormProps> = ({ onSuccess, patientToEdit, refetch }) => {
    const queryClient = useQueryClient();

    const { control, handleSubmit, reset, formState: {errors} } = useForm<PatientCreate>({
        defaultValues: patientToEdit || {
            label: '', first_name: '', last_name: '', gender: Gender.FEMALE, street: '',
            street_number: '', postal_code: '', city: '', birthday: '',
            kilometers_to_travel: 0, email: '', telephone: ''
        }
    });

    const createMutation = useMutation({
        ...createPatientPatientsPostMutation(),
        onSuccess: () => handleSuccess()
    });

    const updateMutation = useMutation({
        ...updatePatientPatientsPatientIdPutMutation(),
        onSuccess: () => handleSuccess()
    });

    const deleteMutation = useMutation({
        ...deletePatientPatientsPatientIdDeleteMutation(),
        onSuccess: () => handleSuccess()
    });

    const handleSuccess = async () => {
        await queryClient.invalidateQueries({ queryKey: getPatientsPatientsGetOptions().queryKey });
        reset();
        onSuccess?.();
    };

    const deletePatient = async (id: number) => {
        await deleteMutation.mutateAsync({
            path: {patient_id: id}
        });
        await refetch();
    }

    const onSubmit = (data: PatientCreate) => {
        if (patientToEdit) {
            updateMutation.mutate({path: { patient_id: patientToEdit.patient_id}, body: data});
        } else {
            createMutation.mutate({ body: data});
        }
    };

    const getFormErrorMessage = (name: keyof PatientCreate) => {
        return errors[name] && <small className="p-error block mt-1">{errors[name]?.message}</small>;
    };

    const accept = async () => {
        await deletePatient(patientToEdit!.patient_id);
        showToast({ severity: 'success', summary: 'Fertig!', detail: 'Patient wurde gelöscht.', life: 3000});
    }

    const {showToast} = useGlobalToast();

    const confirm = () => {
        if (!patientToEdit) {
            return;
        }

        confirmDialog({
            message: `Willst du den Patient ${patientToEdit.first_name} ${patientToEdit.last_name} löschen?`,
            header: 'Löschen?',
            icon: 'pi pi-info-circle',
            defaultFocus: 'reject',
            acceptClassName: 'p-button-danger',
            rejectLabel: "Nein",
            acceptLabel: "Ja",
            accept,
            reject: () => {}

        })
    }

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="grid p-fluid mt-2">
            <ConfirmDialog />
            <div className="col-12 field">
                <label htmlFor="label" className="font-bold">Kürzel</label>
                <Controller
                    name="label"
                    control={control}
                    rules={{
                        required: 'Kürzel ist erforderlich.',
                        pattern: {
                            value: /^[A-Z]{4}$/,
                            message: 'Nur Großbuchstaben (A-Z) erlaubt. 4 Buchstaben!'
                        }
                    }}
                    render={({ field }) => (
                        <>
                            <InputText
                                id={field.name}
                                {...field}
                                maxLength={4}
                                className={errors.label ? 'p-invalid' : ''}
                                disabled={!!patientToEdit}
                                onInput={(e) => {
                                    const target = e.target as HTMLInputElement;
                                    target.value = target.value.toUpperCase().replace(/[^A-Z]/g, '');
                                    field.onChange(target.value);
                                }}
                            />
                            {getFormErrorMessage('label')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="first_name" className="font-bold">Vorname</label>
                <Controller name="first_name" control={control} rules={{ required: 'Vorname ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.first_name ? 'p-invalid' : ''} />
                            {getFormErrorMessage('first_name')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="last_name" className="font-bold">Nachname</label>
                <Controller name="last_name" control={control} rules={{ required: 'Nachname ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.last_name ? 'p-invalid' : ''} />
                            {getFormErrorMessage('last_name')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="gender" className="font-bold">Geschlecht</label>
                <Controller name="gender" control={control}
                            render={({ field }) => <Dropdown id={field.name} {...field} options={Object.values(Gender)} />}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="birthday" className="font-bold">Geburtsdatum</label>
                <Controller
                    name="birthday"
                    control={control}
                    rules={{ required: 'Geburtsdatum ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText
                                id={field.name}
                                type="date"
                                {...field}
                                className={errors.birthday ? 'p-invalid' : ''}
                            />
                            {getFormErrorMessage('birthday')}
                        </>
                    )}
                />
            </div>

            {/* Address with validation messages */}
            <div className="col-12 md:col-9 field">
                <label htmlFor="street" className="font-bold">Straße</label>
                <Controller name="street" control={control} rules={{ required: 'Straße ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.street ? 'p-invalid' : ''} />
                            {getFormErrorMessage('street')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-3 field">
                <label htmlFor="street_number" className="font-bold">Nr.</label>
                <Controller name="street_number" control={control} rules={{ required: 'Nr. ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.street_number ? 'p-invalid' : ''} />
                            {getFormErrorMessage('street_number')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-4 field">
                <label htmlFor="postal_code" className="font-bold">PLZ</label>
                <Controller name="postal_code" control={control} rules={{ required: 'PLZ ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.postal_code ? 'p-invalid' : ''} />
                            {getFormErrorMessage('postal_code')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 md:col-8 field">
                <label htmlFor="city" className="font-bold">Stadt</label>
                <Controller name="city" control={control} rules={{ required: 'Stadt ist erforderlich.' }}
                    render={({ field }) => (
                        <>
                            <InputText id={field.name} {...field} className={errors.city ? 'p-invalid' : ''} />
                            {getFormErrorMessage('city')}
                        </>
                    )}
                />
            </div>

            <div className="col-12 field">
                <label htmlFor="kilometers_to_travel" className="font-bold">Kilometer (Anfahrt)</label>
                <Controller
                    name="kilometers_to_travel"
                    control={control}
                    render={({ field }) => (
                        <InputNumber
                            id={field.name}
                            value={field.value}
                            onValueChange={(e) => field.onChange(e.value ?? 0)}
                            mode="decimal"
                            minFractionDigits={1}
                        />
                    )}
                />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="email" className="font-bold">Email</label>
                <Controller name="email" control={control} render={({ field }) => <InputText id={field.name} {...field} />} />
            </div>

            <div className="col-12 md:col-6 field">
                <label htmlFor="telephone" className="font-bold">Telefon</label>
                <Controller name="telephone" control={control} render={({ field }) => <InputText id={field.name} {...field} />} />
            </div>

            <div className="col-12 flex justify-content-end mt-4 gap-2">
                <>
                    { patientToEdit &&
                        <Button type="button" onClick={confirm} icon="pi pi-trash" label="Löschen" className="w-auto p-button-danger p-button-rounded"/>
                    }
                </>
                <Button
                    type="submit"
                    label="Patient Speichern"
                    icon="pi pi-check"
                    className="w-auto p-button-rounded"
                    loading={updateMutation.isPending || createMutation.isPending}
                />
            </div>
        </form>
    );
};