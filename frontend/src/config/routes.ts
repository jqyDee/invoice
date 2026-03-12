export const ROUTES = {
    HOME : '/',
    LOGIN: '/login',
    PATIENTS : "/patients",
    INVOICES : "/invoices",
    INVOICE_EDIT : "/invoices/create/:id?",
    INVOICE : "/invoices/:id",
    INVOICE_PREVIEW : "/invoices/:id/pdf",
    SETTINGS_GENERAL : "/settings-general",
    SETTINGS_DEFAULTS: "/settings-defaults/:type?",
    THERAPY_PREVIEW: "/therapy/:id/pdf",
    SETTINGS_THERAPY_CLAUSES: "/settings/therapy-clauses",
    PRIVACY_PREVIEW: "/privacy/:id/pdf",
    SETTINGS_PRIVACY_CLAUSES: "/settings/privacy-clauses"
} as const;