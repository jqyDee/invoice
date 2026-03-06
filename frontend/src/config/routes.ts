export const ROUTES = {
    HOME : '/',
    PATIENTS : "/patients",
    INVOICES : "/invoices",
    INVOICE_EDIT : "/invoices/create/:id?",
    INVOICE : "/invoices/:id",
    INVOICE_PREVIEW : "/invoices/:id/pdf",
    SETTINGS_GENERAL : "/settings-general",
    SETTINGS_DEFAULTS: "/settings-defaults/:type?",
} as const;