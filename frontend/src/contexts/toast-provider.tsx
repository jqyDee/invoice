import React, {useCallback, useMemo, useRef} from "react";
import {Toast as PRToast, type ToastMessage} from "primereact/toast";
import {Toast} from "./toast.tsx";

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const toast = useRef<PRToast>(null);

    const showToast = useCallback((message: ToastMessage | ToastMessage[]) => {
        toast.current?.show(message);
    }, [toast]);

    const clearToast = useCallback(() => {
        toast.current?.clear();
    }, [toast]);

    const value = useMemo(() => ({showToast, clearToast}), [showToast, clearToast]);

    return (
        <Toast.Provider value={value}>
            <PRToast ref={toast} />
            {children}
        </Toast.Provider>
    );
};
