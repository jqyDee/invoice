import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getInvoicesInvoicesGetOptions } from "../api/@tanstack/react-query.gen.ts";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { InputSwitch } from "primereact/inputswitch";
import { InvoiceTable } from "./invoice/invoice-table.tsx";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../config/routes.ts";
import {Header} from "../utilities/header.tsx"; // Import Table

interface InvoicesListProps {
    onlyDrafts?: boolean;
}

export const InvoiceListView: React.FC<InvoicesListProps> = ({ onlyDrafts }) => {
    const [search, setSearch] = React.useState("");
    const [debouncedSearch, setDebouncedSearch] = React.useState("");
    const [showDrafts, setShowDrafts] = React.useState(true);

    const navigate = useNavigate();

    React.useEffect(() => {
        const handler = setTimeout(() => setDebouncedSearch(search), 300);
        return () => clearTimeout(handler);
    }, [search]);

    const { data: invoices, isLoading, isError } = useQuery({
        ...getInvoicesInvoicesGetOptions({
            query: { show_drafts: showDrafts, only_drafts: onlyDrafts, search: debouncedSearch }
        })
    });

    if (isError) return <div className="text-red-500 p-5">Fehler beim Laden der Rechnungen.</div>;

    return (
        <div className="flex-column">
            <div className="flex justify-content-between">
                <Header title="Rechnungen"/>
                <div className="flex gap-2 align-items-center">
                    <label>Entwürfe anzeigen</label>
                    <InputSwitch checked={showDrafts} onChange={(e) => setShowDrafts(e.value)} />
                    <Button onClick={() => navigate(generatePath(ROUTES.INVOICE_EDIT, {id : ""}))} icon="pi pi-plus" label="Neue Rechnung" className="p-button-rounded" />
                    <InputText value={search} placeholder="Suche..." onChange={(e) => setSearch(e.target.value)} style={{ minWidth: "20vw" }} />
                </div>
            </div>
            <InvoiceTable invoices={invoices} isLoading={isLoading} />
        </div>
    );
};