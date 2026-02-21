import {PatientListView} from "./src/components/patient-list-view.tsx";
import {ROUTES} from "./src/config/routes.ts";
import {HomepageView} from "./src/components/homepage-view.tsx";
import {InvoiceListView} from "./src/components/invoice-list-view.tsx";
import {InvoiceCreateView} from "./src/components/invoice-create-view.tsx";
import {InvoiceDetailsView} from "./src/components/invoice-details-view.tsx";
import {InvoicePreviewView} from "./src/components/invoice-preview-view.tsx";
import {SettingsGeneralView} from "./src/components/settings-general-view.tsx";
import {SettingsDefaultsView} from "./src/components/settings-defaults-view.tsx";

export const HomeRoute = {
    url: ROUTES.HOME,
    component: HomepageView
}

export const PatientsRoute = {
    url: ROUTES.PATIENTS,
    component: PatientListView
}

export const InvoicesRoute = {
    url: ROUTES.INVOICES,
    component: InvoiceListView
}

export const InvoiceCreateRoute = {
    url: ROUTES.INVOICE_CREATE,
    component: InvoiceCreateView
}

export const InvoiceRoute = {
    url: ROUTES.INVOICE,
    component: InvoiceDetailsView
}

export const InvoicePreviewRoute = {
    url: ROUTES.INVOICE_PREVIEW,
    component: InvoicePreviewView
}

export const SettingsGeneralRoute = {
    url: ROUTES.SETTINGS_GENERAL,
    component: SettingsGeneralView
}

export const SettingsDefaultsRoute = {
    url: ROUTES.SETTINGS_DEFAULTS,
    component: SettingsDefaultsView
}
