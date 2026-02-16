import {useContext} from "react";
import {Toast} from "../contexts/toast.tsx"

export const useGlobalToast = () => {
    const context = useContext(Toast);
    if (!context) {
        throw new Error('useGlobalToast must be used within a ToastProvider');
    }
    return context;
};
