import {ROUTES} from "./routes.ts";
import type {MenuItem} from "primereact/menuitem";
import {generatePath} from "react-router-dom";

export const menu: MenuItem[] = [
    {
        label: 'Startseite', icon: 'pi pi-home', url: ROUTES.HOME
    },
    {
        label: 'Patienten', icon: 'pi pi-user', url: ROUTES.PATIENTS
    },
    {
        label: 'Rechnungen', icon: 'pi pi-receipt', url: ROUTES.INVOICES
    },
    {
        label: 'Einstellungen', icon: 'pi pi-cog', items: [
            {
                label: 'Allgemein', icon: 'pi pi-id-card', url: ROUTES.SETTINGS_GENERAL
            },
            {
                label: 'Standardleistungen', icon: 'pi pi-thumbtack', url: generatePath(ROUTES.SETTINGS_DEFAULTS, { type: '' })
            },
        ]
    },
];
