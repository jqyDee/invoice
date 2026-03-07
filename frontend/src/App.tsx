import React from "react"
import {createBrowserRouter, RouterProvider} from "react-router-dom"
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import "primereact/resources/themes/mdc-light-indigo/theme.css";
import "primeflex/primeflex.css"
import {
    HomeRoute,
    InvoiceCreateRoute,
    InvoicePreviewRoute,
    InvoiceRoute,
    InvoicesRoute,
    PatientsRoute, PrivacyPreviewRoute, SettingsDefaultsRoute, SettingsGeneralRoute, SettingsPrivacyClausesRoute,
    SettingsTherapyClausesRoute, TherapyPreviewRoute
} from "../routes.ts";
import {MainLayout} from "./components/layouts/main-layout.tsx";
import {CardLayout} from "./components/layouts/card-layout.tsx";
import {ToastProvider} from "./contexts/toast-provider.tsx";

const client = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 5,    // Data is "fresh" for 5 minutes
        },
    },
});

const router = createBrowserRouter([
    {
        element: <MainLayout />,
        children: [
            {
                element: <CardLayout />,
                children: [
                    { path: HomeRoute.url, Component: HomeRoute.component },
                    { path: PatientsRoute.url, Component: PatientsRoute.component },
                    { path: InvoicesRoute.url, Component: InvoicesRoute.component },
                    { path: InvoiceCreateRoute.url, Component: InvoiceCreateRoute.component },
                    { path: InvoiceRoute.url, Component: InvoiceRoute.component },
                    { path: SettingsGeneralRoute.url, Component: SettingsGeneralRoute.component },
                    { path: SettingsDefaultsRoute.url, Component: SettingsDefaultsRoute.component },
                    { path: SettingsTherapyClausesRoute.url, Component: SettingsTherapyClausesRoute.component },
                    { path: SettingsPrivacyClausesRoute.url, Component: SettingsPrivacyClausesRoute.component },
                ],
            },
            // Preview pages — no Card, but still inside MainLayout
            { path: InvoicePreviewRoute.url, Component: InvoicePreviewRoute.component },
            { path: TherapyPreviewRoute.url, Component: TherapyPreviewRoute.component },
            { path: PrivacyPreviewRoute.url, Component: PrivacyPreviewRoute.component },
        ],
    },
]);

const App: React.FC = () => {
    return (
        <QueryClientProvider client={client}>
            <ToastProvider>
                <RouterProvider router={router} />
            </ToastProvider>
        </QueryClientProvider>
    )
}
export default App