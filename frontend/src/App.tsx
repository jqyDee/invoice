import React from "react"
import {Routes, Route, BrowserRouter} from "react-router-dom"
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import "primereact/resources/themes/mdc-light-indigo/theme.css";
import "primeflex/primeflex.css"
import {
    HomeRoute,
    InvoiceCreateRoute,
    InvoicePreviewRoute,
    InvoiceRoute,
    InvoicesRoute,
    PatientsRoute, SettingsDefaultsRoute, SettingsGeneralRoute
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

const App: React.FC = () => {
    return (
        <QueryClientProvider client={client}>
            <BrowserRouter>
                <ToastProvider>
                    <Routes>
                        <Route element={<MainLayout />}>
                            {/* Standard Pages wrapped in a Card */}
                            <Route element={<CardLayout />}>
                                <Route path={HomeRoute.url} Component={HomeRoute.component}/>
                                <Route path={PatientsRoute.url} Component={PatientsRoute.component} />
                                <Route path={InvoicesRoute.url} Component={InvoicesRoute.component} />
                                <Route path={InvoiceCreateRoute.url} Component={InvoiceCreateRoute.component} />
                                <Route path={InvoiceRoute.url} Component={InvoiceRoute.component} />
                                <Route path={SettingsGeneralRoute.url} Component={SettingsGeneralRoute.component} />
                                <Route path={SettingsDefaultsRoute.url} Component={SettingsDefaultsRoute.component} />
                            </Route>

                            {/* Preview Page - No Card, but still has NavbarView */}
                            <Route path={InvoicePreviewRoute.url} Component={InvoicePreviewRoute.component} />
                        </Route>
                    </Routes>
                </ToastProvider>
            </BrowserRouter>
        </QueryClientProvider>
    )
}
export default App