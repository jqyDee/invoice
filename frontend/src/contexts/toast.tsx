import React, {createContext, useCallback, useContext, useMemo, useRef} from 'react';
import { Toast as PRToast, type ToastMessage } from 'primereact/toast';

interface ToastContextType {
    showToast: (message: ToastMessage | ToastMessage[]) => void;
    clearToast: () => void;
}

const Toast = createContext<ToastContextType | null>(null);

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

export const useGlobalToast = () => {
    const context = useContext(Toast);
    if (!context) {
        throw new Error('useGlobalToast must be used within a ToastProvider');
    }
    return context;
};