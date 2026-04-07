import React from "react";
import {useQuery} from "@tanstack/react-query";
import {getInvoicesInvoicesGetOptions} from "../api/@tanstack/react-query.gen.ts";
import {Button} from "primereact/button";
import {InputText} from "primereact/inputtext";
import {InputSwitch} from "primereact/inputswitch";
import {MultiSelect} from "primereact/multiselect";
import {InvoiceTable} from "./invoice/invoice-table.tsx";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "../config/routes.ts";
import {Header} from "../utilities/header.tsx";
import {IconField} from "primereact/iconfield";
import {InputIcon} from "primereact/inputicon";
import {InvoiceType} from "../api";

interface InvoicesListProps {
    onlyDrafts?: boolean;
}

const currentYear = new Date().getFullYear();
const yearOptions = Array.from({length: currentYear - 2019}, (_, i) => currentYear - i).map(y => ({label: String(y), value: y}));
const monthOptions = [
    {label: 'Januar', value: 1}, {label: 'Februar', value: 2}, {label: 'März', value: 3},
    {label: 'April', value: 4}, {label: 'Mai', value: 5}, {label: 'Juni', value: 6},
    {label: 'Juli', value: 7}, {label: 'August', value: 8}, {label: 'September', value: 9},
    {label: 'Oktober', value: 10}, {label: 'November', value: 11}, {label: 'Dezember', value: 12},
];
const typeOptions = Object.values(InvoiceType).map(t => ({label: t, value: t}));

export const InvoiceListView: React.FC<InvoicesListProps> = ({onlyDrafts}) => {
    const [search, setSearch] = React.useState("");
    const [debouncedSearch, setDebouncedSearch] = React.useState("");
    const [showDrafts, setShowDrafts] = React.useState(true);
    const [showFilters, setShowFilters] = React.useState(false);
    const [selectedYears, setSelectedYears] = React.useState<number[]>([currentYear]);
    const [selectedMonths, setSelectedMonths] = React.useState<number[]>([]);
    const [selectedTypes, setSelectedTypes] = React.useState<InvoiceType[]>([]);
    const [page, setPage] = React.useState(1);
    const [pageSize, setPageSize] = React.useState(20);

    const navigate = useNavigate();

    React.useEffect(() => {
        const handler = setTimeout(() => setDebouncedSearch(search), 300);
        return () => clearTimeout(handler);
    }, [search]);

    const resetPage = () => setPage(1);

    const {data, isLoading, isError} = useQuery({
        ...getInvoicesInvoicesGetOptions({
            query: {
                show_drafts: showDrafts,
                only_drafts: onlyDrafts,
                search: debouncedSearch || undefined,
                invoice_types: selectedTypes.length ? selectedTypes : undefined,
                years: selectedYears.length ? selectedYears : undefined,
                months: selectedMonths.length ? selectedMonths : undefined,
                page,
                size: pageSize,
            }
        })
    });

    if (isError) return <div className="text-red-500 p-5">Fehler beim Laden der Rechnungen.</div>;

    return (
        <div className="flex-column">
            <div className="flex flex-column md:flex-row justify-content-between md:align-items-center gap-3">
                <Header title="Rechnungen"/>

                <div className="flex gap-2 w-full md:w-auto">
                    <Button
                        icon="pi pi-filter"
                        className="p-button-outlined md:hidden flex-shrink-0"
                        onClick={() => setShowFilters(!showFilters)}
                        aria-label="Filter"
                    />

                    <IconField iconPosition="left" className="w-full">
                        <InputIcon className="pi pi-search"/>
                        <InputText
                            value={search}
                            placeholder="Suche..."
                            onChange={(e) => { setSearch(e.target.value); resetPage(); }}
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

            <div
                className={`surface-100 p-3 border-round flex-column md:flex-row align-items-start md:align-items-center gap-4 ${showFilters ? 'flex' : 'hidden md:flex'}`}>
                <div className="flex align-items-center gap-2">
                    <InputSwitch
                        inputId="draft-switch"
                        checked={showDrafts}
                        onChange={(e) => { setShowDrafts(e.value); resetPage(); }}
                    />
                    <label htmlFor="draft-switch" className="cursor-pointer font-medium">
                        Entwürfe anzeigen
                    </label>
                </div>

                <MultiSelect
                    value={selectedYears}
                    options={yearOptions}
                    onChange={(e) => { setSelectedYears(e.value); resetPage(); }}
                    placeholder="Jahr"
                    className="w-10rem"
                    maxSelectedLabels={2}
                />

                <MultiSelect
                    value={selectedMonths}
                    options={monthOptions}
                    onChange={(e) => { setSelectedMonths(e.value); resetPage(); }}
                    placeholder="Monat"
                    className="w-10rem"
                    maxSelectedLabels={2}
                />

                <MultiSelect
                    value={selectedTypes}
                    options={typeOptions}
                    onChange={(e) => { setSelectedTypes(e.value); resetPage(); }}
                    placeholder="Typ"
                    className="w-8rem"
                    maxSelectedLabels={3}
                />
            </div>

            <InvoiceTable
                invoices={data?.items}
                isLoading={isLoading}
                totalRecords={data?.total ?? 0}
                page={page}
                pageSize={pageSize}
                onPageChange={(p, s) => { setPage(p); setPageSize(s); }}
            />
        </div>
    );
};