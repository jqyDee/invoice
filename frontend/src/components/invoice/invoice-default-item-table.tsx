import React from "react";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import type {DefaultInvoiceItem, InvoiceCreate, InvoiceUpdate} from "../../api";
import {InputSwitch} from "primereact/inputswitch";
import {useQuery} from "@tanstack/react-query";
import {getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions} from "../../api/@tanstack/react-query.gen.ts";
import {Fieldset} from "primereact/fieldset";
import {Tag} from "primereact/tag";

interface InvoiceDefaultItemTableProps {
    invoice: InvoiceCreate | InvoiceUpdate;
    onChange: (fields: Partial<InvoiceCreate | InvoiceUpdate>) => void;
}

export const InvoiceDefaultItemTable: React.FC<InvoiceDefaultItemTableProps> = ({invoice, onChange}) => {
    const {data: availableDefaults} = useQuery(getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
        query: {invoice_type: invoice.type}
    }));

    const toggleDefault = (id: number) => {
        const currentIds = invoice.default_item_ids || [];
        const nextIds = currentIds.includes(id) ? currentIds.filter(i => i !== id) : [...currentIds, id];
        onChange({default_item_ids: nextIds});
    };

    const fieldsetLegend = (
        <div className="flex align-items-center gap-2">
            <span>Standard-Leistungen</span>
            {invoice.default_item_ids && (
                <Tag value={invoice.default_item_ids.length} severity="info" rounded/>
            )}
        </div>
    )

    return (
        <Fieldset
            legend={fieldsetLegend}
            toggleable
            collapsed={true}
        >
            <DataTable
                value={availableDefaults}
                key={`defaults-table-${invoice.default_item_ids?.length || 0}`}
                showGridlines
                className="p-datatable-sm p-datatable-striped w-full"
                emptyMessage="Keine Standard-Leistungen vorhanden."
            >
                <Column
                    header="Beschreibung"
                    field="description"
                />
                <Column
                    header="Aktiv"
                    body={(i: DefaultInvoiceItem) =>
                        <InputSwitch
                            checked={invoice.default_item_ids?.includes(i.default_item_id) || false}
                            onChange={() => toggleDefault(i.default_item_id)}
                        />
                    }
                />
            </DataTable>
        </Fieldset>
    )
}