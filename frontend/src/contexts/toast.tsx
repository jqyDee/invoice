import {createContext} from 'react';
import {type ToastMessage } from 'primereact/toast';

interface ToastContextType {
    showToast: (message: ToastMessage | ToastMessage[]) => void;
    clearToast: () => void;
}

export const Toast = createContext<ToastContextType | null>(null);

