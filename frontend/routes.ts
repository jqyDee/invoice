import {PatientListView} from "./src/components/patient-list-view.tsx";
import {ROUTES} from "./src/config/routes.ts";
import {HomepageView} from "./src/components/homepage-view.tsx";
import {InvoiceListView} from "./src/components/invoice-list-view.tsx";
import {InvoiceEditView} from "./src/components/invoice-edit-view.tsx";
import {InvoiceDetailsView} from "./src/components/invoice-details-view.tsx";
import {SettingsGeneralView} from "./src/components/settings-general-view.tsx";
import {SettingsDefaultsView} from "./src/components/settings-defaults-view.tsx";
import {InvoicePreviewView} from "./src/components/invoice-preview-view.tsx";
import {TherapyPreviewView} from "./src/components/therapy-preview-view.tsx";
import {SettingsTherapyClausesView} from "./src/components/settings-therapy-clauses-view.tsx";

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
    url: ROUTES.INVOICE_EDIT,
    component: InvoiceEditView
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

export const TherapyPreviewRoute = {
    url: ROUTES.THERAPY_PREVIEW,
    component: TherapyPreviewView
}

export const SettingsTherapyClausesRoute = {
    url: ROUTES.SETTINGS_THERAPY_CLAUSES,
    component: SettingsTherapyClausesView
}
