import React from "react";
import {useQuery} from "@tanstack/react-query";
import {
    getAvailableYearsEndpointTaxReportAvailableYearsGetOptions,
    getTaxReportEndpointTaxReportYearAmountsGetOptions,
} from "../api/@tanstack/react-query.gen.ts";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import {Button} from "primereact/button";
import {ListBox} from "primereact/listbox";
import {Tag} from "primereact/tag";
import {Header} from "../utilities/header.tsx";
import type {TaxReportRow} from "../api";
import {toGermanDateString} from "../utilities/local-date-string.ts";
import {enforceNonNull} from "../utilities/enforce-non-null.ts";

export const TaxReportView: React.FC = () => {
    const {data: availableYears, isLoading: yearsLoading} = useQuery({
        ...getAvailableYearsEndpointTaxReportAvailableYearsGetOptions(),
    });

    const [selectedYear, setSelectedYear] = React.useState<number | null>(null);

    React.useEffect(() => {
        if (availableYears && availableYears.length > 0 && selectedYear === null) {
            setSelectedYear(availableYears[0]);
        }
    }, [availableYears, selectedYear]);

    const {data: report, isLoading: rowsLoading} = useQuery({
        ...getTaxReportEndpointTaxReportYearAmountsGetOptions({path: {year: selectedYear!}}),
        enabled: selectedYear !== null,
    });

    const rows = report?.rows ?? [];
    const totalIncome = report?.total_income ?? 0;
    const totalKm = report?.total_kilometers_travelled ?? 0;

    const handleCsvDownload = async (type: "amounts" | "travel") => {
        if (selectedYear === null) return;
        const token = localStorage.getItem("token");
        const response = await fetch(`/api/tax-report/${selectedYear}/csv/${type}`, {
            headers: {Authorization: `Bearer ${token}`},
        });
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `steuer_${type}_${selectedYear}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const yearOptions = (availableYears ?? []).map((y) => ({label: String(y), value: y}));

    return (
        <div className="flex flex-column md:flex-row gap-3 w-full">

            <div className="surface-100 border-round p-2 w-full md:w-16rem flex-shrink-0">
                {yearsLoading ? (
                    <div className="p-2 text-sm text-color-secondary">Laden...</div>
                ) : (
                    <ListBox
                        value={selectedYear}
                        options={yearOptions}
                        onChange={(e: { value: number }) => setSelectedYear(e.value)}
                        className="border-none w-full"
                        listStyle={{maxHeight: '200px'}}
                    />
                )}
            </div>

            <div className="flex flex-column gap-3 flex-1 overflow-hidden" style={{minWidth: 0}}>
                <div className="flex flex-wrap justify-content-between align-items-center gap-2">
                    <Header title={selectedYear ? `Steuerbericht ${selectedYear}` : "Steuerbericht"}/>
                    <div className="flex gap-2">
                        <Button
                            icon="pi pi-download"
                            label="CSV Beträge"
                            className="p-button-outlined"
                            onClick={() => handleCsvDownload("amounts")}
                            disabled={selectedYear === null || rowsLoading}
                        />
                        <Button
                            icon="pi pi-download"
                            label="CSV Km"
                            className="p-button-outlined"
                            onClick={() => handleCsvDownload("travel")}
                            disabled={selectedYear === null || rowsLoading}
                        />
                    </div>
                </div>

                <div className="flex flex-wrap gap-2">
                    <Tag severity="success" value={`Einnahmen: ${totalIncome.toFixed(2)} €`}/>
                    <Tag severity="info" value={`Km gesamt: ${totalKm.toFixed(1)} km`}/>
                </div>

                <div className="w-full overflow-x-auto border-round">
                    <DataTable
                        value={rows ?? []}
                        loading={rowsLoading}
                        stripedRows
                        showGridlines
                        size="small"
                        removableSort
                        paginator
                        rows={20}
                        emptyMessage="Kein Steuerbericht verfügbar."
                        className="min-w-max" // Ensures table doesn't squash columns unreadably small
                    >
                        <Column field="invoice_number" header="Rechnungsnummer" sortable/>
                        <Column field="invoice_type" header="Rechnungstyp" sortable/>
                        <Column field="invoice_date" header="Rechnungsdatum" sortable
                                body={(e: TaxReportRow) => toGermanDateString(new Date(e.invoice_date))}/>
                        <Column field="paid_date" header="Bezahlt am" sortable
                                body={(e: TaxReportRow) => toGermanDateString(new Date(enforceNonNull(e.paid_date)))}/>
                        <Column field="kilometers_at_billing" header="Km bei Abrechnung" sortable/>
                        <Column field="total_kilometers_travelled" header="Gesamte Km" sortable/>
                        <Column field="number_of_treatment_dates" header="Behandlungstermine" sortable/>
                        <Column
                            field="invoice_total"
                            header="Rechnungsbetrag (€)"
                            sortable
                            body={(row) => row.invoice_total.toFixed(2)}
                        />
                    </DataTable>
                </div>
            </div>
        </div>
    );
};
