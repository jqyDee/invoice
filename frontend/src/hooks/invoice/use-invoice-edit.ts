import React, {useRef, useMemo, useEffect} from "react";
import {Stepper} from "primereact/stepper";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {generatePath, useBlocker, useNavigate, useParams} from "react-router-dom";
import {
    createInvoiceInvoicesPostMutation,
    getInvoicesInvoicesGetQueryKey,
    getInvoiceInvoicesInvoiceIdGetOptions,
    updateInvoiceInvoicesInvoiceIdPatchMutation,
    getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions,
    getInvoiceInvoicesInvoiceIdGetQueryKey,
} from "../../api/@tanstack/react-query.gen.ts";
import {ROUTES} from "../../config/routes.ts";
import {toLocalDateString} from "../../utilities/local-date-string.ts";
import {useGlobalToast} from "../use-global-toast.ts";
import {extractApiError} from "../../utilities/api-error.ts";
import {type InvoiceCreate, InvoiceType, type InvoiceUpdate} from "../../api";

export function useInvoiceEdit() {
    const {id} = useParams();
    const navigate = useNavigate();
    const {showToast} = useGlobalToast();
    const queryClient = useQueryClient();

    const stepperRef = useRef<Stepper>(null);
    const initialInvoiceRef = useRef<InvoiceCreate | InvoiceUpdate | null>(null);
    const skipBlockerRef = useRef(false);
    const historyActionRef = useRef<string | null>(null);

    const [activeStep, setActiveStep] = React.useState(0);
    const [invoice, setInvoice] = React.useState<InvoiceCreate | InvoiceUpdate>({
        patient_id: 0,
        invoice_date: toLocalDateString(new Date()),
        type: InvoiceType.HP,
        user_items: [],
        default_item_ids: [],
        dates: [],
        diagnosis: "",
    });

    const {data: invoiceToUpdate, isLoading} = useQuery({
        ...getInvoiceInvoicesInvoiceIdGetOptions({
            path: {invoice_id: parseInt(id!)},
        }),
        enabled: !!id,
        retry: false,
    });

    const {data: availableDefaults} = useQuery(
        getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
            query: {invoice_type: invoice.type},
        })
    );

    useEffect(() => {
        if (id && invoiceToUpdate) {
            const loaded: InvoiceUpdate = {
                patient_id: invoiceToUpdate.patient_id,
                invoice_date: invoiceToUpdate.invoice_date,
                type: invoiceToUpdate.type,
                user_items: invoiceToUpdate.user_items,
                default_item_ids: invoiceToUpdate.default_items.map(d => d.default_item_id),
                dates: invoiceToUpdate.dates,
                diagnosis: invoiceToUpdate.diagnosis,
            };
            setInvoice(loaded);
            if (!initialInvoiceRef.current) {
                initialInvoiceRef.current = loaded;
            }
        } else if (!id && availableDefaults) {
            const activeGlobalIds = availableDefaults
                .filter(d => d.is_active_global)
                .map(d => d.default_item_id);
            setInvoice(prev => ({...prev, default_item_ids: activeGlobalIds}));
        }
    }, [id, invoiceToUpdate, availableDefaults]);

    const updateInvoice = (fields: Partial<InvoiceCreate | InvoiceUpdate>) => {
        setInvoice(prev => ({...prev, ...fields}));
    };

    const isDirty = useMemo(() => {
        if (initialInvoiceRef.current) {
            return JSON.stringify(invoice) !== JSON.stringify(initialInvoiceRef.current);
        }
        return invoice.patient_id !== 0;
    }, [invoice]);

    const goNext = () => {
        stepperRef.current?.nextCallback();
        setActiveStep(s => s + 1);
    };
    const goPrev = () => {
        stepperRef.current?.prevCallback();
        setActiveStep(s => s - 1);
    };

    const handleSuccess = async (isUpdate: boolean) => {
        showToast({
            severity: "success",
            summary: "Fertig!",
            detail: `Rechnung wurde ${isUpdate ? "aktualisiert" : "gespeichert"}.`,
            life: 3000,
        });
        await queryClient.invalidateQueries({queryKey: getInvoicesInvoicesGetQueryKey()});
    };

    const createMutation = useMutation({
        ...createInvoiceInvoicesPostMutation(),
        onSuccess: () => handleSuccess(false),
    });

    const updateMutation = useMutation({
        ...updateInvoiceInvoicesInvoiceIdPatchMutation(),
        onSuccess: () => handleSuccess(true),
    });

    const doSave = async (options?: { asDraft?: boolean }): Promise<number> => {
        let result;
        if (id) {
            result = await updateMutation.mutateAsync({
                path: {invoice_id: parseInt(id)},
                body: {...(invoice as InvoiceUpdate), save_as_draft: options?.asDraft ?? false},
            });
        } else {
            result = await createMutation.mutateAsync({
                body: {...(invoice as InvoiceCreate), save_as_draft: options?.asDraft ?? false},
            });
        }
        await queryClient.invalidateQueries({
            queryKey: getInvoiceInvoicesInvoiceIdGetQueryKey({
                path: {invoice_id: result.invoice_id},
            }),
        });
        return result.invoice_id;
    };

    const handleSave = async () => {
        try {
            const invoiceId = await doSave();
            skipBlockerRef.current = true;
            navigate(generatePath(ROUTES.INVOICE, {id: invoiceId.toString()}));
        } catch (error) {
            showToast({
                severity: "error",
                summary: "Fehler",
                detail: `Rechnung konnte nicht gespeichert werden. ${extractApiError(error)}`
            });
        }
    };

    const handleSaveDraft = async () => {
        skipBlockerRef.current = true;
        try {
            await doSave({asDraft: true});
            blocker.proceed?.();
        } catch (error) {
            skipBlockerRef.current = false;
            showToast({
                severity: "error",
                summary: "Fehler",
                detail: `Rechnung konnte nicht gespeichert werden. ${extractApiError(error)}`
            });
        }
    };

    const blocker = useBlocker(({historyAction}) => {
        if (skipBlockerRef.current) return false;
        historyActionRef.current = historyAction;
        if (activeStep > 0 && historyAction === "POP") return true;
        return isDirty;
    });

    useEffect(() => {
        if (blocker.state !== "blocked") return;
        if (activeStep > 0 && historyActionRef.current === "POP") {
            goPrev();
            blocker.reset();
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [blocker.state]);

    useEffect(() => {
        const handler = (e: BeforeUnloadEvent) => {
            if (isDirty) e.preventDefault();
        };
        window.addEventListener("beforeunload", handler);
        return () => window.removeEventListener("beforeunload", handler);
    }, [isDirty]);

    const showLeaveDialog =
        blocker.state === "blocked" &&
        !(activeStep > 0 && historyActionRef.current === "POP");

    return {
        id,
        invoice,
        updateInvoice,
        isLoading,
        isDirty,
        stepperRef,
        activeStep,
        goNext,
        goPrev,
        handleSave,
        blocker,
        showLeaveDialog,
        handleSaveDraft,
    };
}
