import {ROUTES} from "./routes.ts";
import type {MenuItem} from "primereact/menuitem";
import {generatePath} from "react-router-dom";

export const buildMenu = (navigate: (path: string) => void): MenuItem[] => [
    {
        label: 'Startseite', icon: 'pi pi-home', command: () => navigate(ROUTES.HOME)
    },
    {
        label: 'Patienten', icon: 'pi pi-user', command: () => navigate(ROUTES.PATIENTS)
    },
    {
        label: 'Rechnungen', icon: 'pi pi-receipt', command: () => navigate(ROUTES.INVOICES)
    },
    {
        label: 'Einstellungen', icon: 'pi pi-cog', items: [
            {
                label: 'Allgemein', icon: 'pi pi-id-card', command: () => navigate(ROUTES.SETTINGS_GENERAL)
            },
            {
                label: 'Standardleistungen', icon: 'pi pi-thumbtack', command: () => navigate(generatePath(ROUTES.SETTINGS_DEFAULTS, { type: '' }))
            },
            {
                label: 'Therapie-Klauseln', icon: 'pi pi-file-edit', command: () => navigate(ROUTES.SETTINGS_THERAPY_CLAUSES)
            },
            {
                label: 'Datenschutz-Klauseln', icon: 'pi pi-shield', command: () => navigate(ROUTES.SETTINGS_PRIVACY_CLAUSES)
            },
        ]
    },
];
