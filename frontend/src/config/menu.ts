import {ROUTES} from "./routes.ts";
import type {MenuItem} from "primereact/menuitem";

export const menu: MenuItem[] = [
    {
        label: 'Home', icon: 'pi pi-home', url: ROUTES.HOME
    },
    {
        label: 'Patienten', icon: 'pi pi-user', url: ROUTES.PATIENTS
    },
    {
        label: 'Rechnungen', icon: 'pi pi-receipt', url: ROUTES.INVOICES
    }
];
