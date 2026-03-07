import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getInvoicesInvoicesGetOptions } from "../api/@tanstack/react-query.gen.ts";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";
import { InputSwitch } from "primereact/inputswitch";
import { InvoiceTable } from "./invoice/invoice-table.tsx";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../config/routes.ts";
import {Header} from "../utilities/header.tsx";
import {IconField} from "primereact/iconfield";
import {InputIcon} from "primereact/inputicon";

interface InvoicesListProps {
    onlyDrafts?: boolean;
}

export const InvoiceListView: React.FC<InvoicesListProps> = ({ onlyDrafts }) => {
    const [search, setSearch] = React.useState("");
    const [debouncedSearch, setDebouncedSearch] = React.useState("");
    const [showDrafts, setShowDrafts] = React.useState(true);
    const [showFilters, setShowFilters] = React.useState(false);

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
            <div className="flex flex-column md:flex-row justify-content-between md:align-items-center gap-3">
                <Header title="Rechnungen" />

                <div className="flex gap-2 w-full md:w-auto">
                    <Button
                        icon="pi pi-filter"
                        className="p-button-outlined md:hidden flex-shrink-0"
                        onClick={() => setShowFilters(!showFilters)}
                        aria-label="Filter"
                    />

                    <IconField iconPosition="left" className="w-full">
                        <InputIcon className="pi pi-search" />
                        <InputText
                            value={search}
                            placeholder="Suche..."
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full md:w-15rem"
                        />
                    </IconField>

                    <Button
                        onClick={() => navigate(generatePath(ROUTES.INVOICE_EDIT, {id: ""}))}
                        icon="pi pi-plus"
                        label="Neu"
                        className="p-button-rounded flex-shrink-0"
                    />
                </div>
            </div>

            <div className={`surface-100 p-3 border-round flex-column md:flex-row align-items-start md:align-items-center gap-4 ${showFilters ? 'flex' : 'hidden md:flex'}`}>
                <div className="flex align-items-center gap-2">
                    <InputSwitch
                        inputId="draft-switch"
                        checked={showDrafts}
                        onChange={(e) => setShowDrafts(e.value)}
                    />
                    <label htmlFor="draft-switch" className="cursor-pointer font-medium">
                        Entwürfe anzeigen
                    </label>
                </div>

                {/* You can easily add more filters here later (e.g., date pickers, status dropdowns) */}
            </div>

            <InvoiceTable invoices={invoices} isLoading={isLoading} />
        </div>
    );
};