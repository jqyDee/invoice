import React from 'react';
import {Controller, useForm} from 'react-hook-form';
import {InputText} from 'primereact/inputtext';
import {Dropdown} from 'primereact/dropdown';
import {Button} from 'primereact/button';
import {InputNumber} from "primereact/inputnumber";
import {useMutation, useQueryClient} from '@tanstack/react-query';
import {
    createPatientPatientsPostMutation,
    deletePatientPatientsPatientIdDeleteMutation,
    getPatientsPatientsGetOptions,
    updatePatientPatientsPatientIdPutMutation,
} from '../../api/@tanstack/react-query.gen.ts';
import {Gender, type HttpValidationError, type Patient, type PatientCreate} from '../../api';
import {confirmDialog, ConfirmDialog} from "primereact/confirmdialog";
import {useGlobalToast} from "../../hooks/use-global-toast.ts";
import {toGermanGender} from "../../utilities/gender.ts";

interface PatientFormProps {
    onSuccess?: () => void;
    patientToEdit?: Patient | null;
}

export const PatientForm: React.FC<PatientFormProps> = ({ onSuccess, patientToEdit }) => {
    const queryClient = useQueryClient();

    const { control, handleSubmit, reset, formState: {errors}, watch, setValue } = useForm<PatientCreate>({
        defaultValues: patientToEdit || {
            label: '', first_name: '', last_name: '', gender: Gender.MALE, street: '',
            street_number: '', postal_code: '', city: '', birthday: '',
            kilometers_to_travel: 0, email: '', telephone: ''
        }
    });

    const watchedFirstname = watch('first_name')
    const watchedLastname = watch('last_name')

    React.useEffect(() => {
        const fName = (watchedFirstname || '').trim();
        const lName = (watchedLastname || '').trim();

        const generatedLabel = (
            lName.substring(0, 2) +
                fName.substring(0, 2)
        ).toUpperCase();

        setValue('label', generatedLabel, {shouldValidate: true});
    }, [watchedLastname, watchedFirstname, setValue, patientToEdit])

    const createMutation = useMutation({
        ...createPatientPatientsPostMutation(),
        onSuccess: () => handleSuccess(),
        onError: (error) => handleError(error)
    });

    const updateMutation = useMutation({
        ...updatePatientPatientsPatientIdPutMutation(),
        onSuccess: () => handleSuccess(),
        onError: (error) => handleError(error)
    });

    const deleteMutation = useMutation({
        ...deletePatientPatientsPatientIdDeleteMutation(),
        onSuccess: () => handleSuccess(true),
        onError: (error) => handleError(error)
    });

    const handleSuccess = async (isDelete?: boolean) => {
        await queryClient.invalidateQueries({ queryKey: getPatientsPatientsGetOptions().queryKey });
        reset();
        showToast({ severity: 'success', summary: 'Erfolg', detail: `Patientendaten ${isDelete ? "gelöscht" : "gespeichert"}.`, life: 3000 });
        onSuccess?.();
    };

    const handleError = (error: HttpValidationError) => {
        reset();
        showToast({ severity: 'error', summary: 'Error', detail: `Patientendaten konnten nicht gespeichert werden. ${JSON.stringify(error.detail)}`, life: 3000 });
    }

    const deletePatient = async (id: number) => {
        await deleteMutation.mutateAsync({
            path: {patient_id: id}
        });
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
                <label htmlFor="label" className="font-bold">Kürzel (abgeleitet aus Vor- und Nachname)</label>
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
                                disabled={true}
                                className={errors.first_name ? 'p-invalid' : ''}
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
                            render={({ field }) =>
                                <Dropdown
                                    id={field.name}
                                    {...field}
                                    options={Object.values(Gender).map((g) => ({
                                        label: toGermanGender(g),
                                        value: g
                                    }))}
                                />
                            }
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