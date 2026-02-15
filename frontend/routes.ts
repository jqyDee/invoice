import {PatientList} from "./src/components/patient-list.tsx";
import {ROUTES} from "./src/config/routes.ts";
import {Homepage} from "./src/components/homepage.tsx";
import {InvoicesList} from "./src/components/invoices-list.tsx";
import {InvoiceCreateView} from "./src/components/invoice-create-view.tsx";
import {InvoiceDetails} from "./src/components/invoice-details.tsx";
import {InvoicePreview} from "./src/components/invoice-preview.tsx";

export const HomeRoute = {
    url: ROUTES.HOME,
    component: Homepage
}

export const PatientsRoute = {
    url: ROUTES.PATIENTS,
    component: PatientList
}

export const InvoicesRoute = {
    url: ROUTES.INVOICES,
    component: InvoicesList
}

export const InvoiceCreateRoute = {
    url: ROUTES.INVOICE_CREATE,
    component: InvoiceCreateView
}

export const InvoiceRoute = {
    url: ROUTES.INVOICE,
    component: InvoiceDetails
}

export const InvoicePreviewRoute = {
    url: ROUTES.INVOICE_PREVIEW,
    component: InvoicePreview
}
