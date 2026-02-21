import React from "react";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {
    getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions,
    updateDefaultInvoiceItemInvoiceItemsDefaultsItemIdPatchMutation,
} from "../../api/@tanstack/react-query.gen.ts";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import {TabMenu} from "primereact/tabmenu";
import {useSettingsDefaultsMenu} from "../../config/settings-defaults-menu.ts";
import {useParams} from "react-router-dom";
import {type DefaultInvoiceItem, DefaultInvoiceItemPosition, InvoiceType} from "../../api";
import {InputSwitch} from "primereact/inputswitch";


export const DefaultItemTable: React.FC = () => {
    const queryClient = useQueryClient();
    const menuItems = useSettingsDefaultsMenu();
    const { type } = useParams<{ type?: string }>();

    const { data: defaultItems, isLoading } = useQuery({
        ...getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
            query: { invoice_type: type ? type as InvoiceType : null}
        }),
        retry: false,
    });

    const updateMutation = useMutation({
        ...updateDefaultInvoiceItemInvoiceItemsDefaultsItemIdPatchMutation(),
        onSuccess: async () => {
            await queryClient.invalidateQueries({
                queryKey: getDefaultInvoiceItemsInvoiceItemsDefaultsGetOptions({
                    query: { invoice_type: type ? type as InvoiceType : null }
                }).queryKey
            });
        }
    });

    const activeTemplate = (rowData: DefaultInvoiceItem) => {
        return (
            <InputSwitch
                checked={rowData.is_active_global}
                onChange={(e) => {
                    updateMutation.mutate({
                        path: { item_id: rowData.default_item_id },
                        body: { is_active_global: e.value }
                    });
                }}
            />
        );
    };

    const positionToGerman = (p: DefaultInvoiceItemPosition): string => {
        if (p === DefaultInvoiceItemPosition.BOTH) return "Vorne & Hinten"
        else if (p === DefaultInvoiceItemPosition.APPEND) return "Hinten"
        else return "Vorne"
    }

    return (
        <div>
            <TabMenu model={menuItems}/>
            <DataTable
                value={defaultItems}
                paginator
                key="default_item_id"
                rows={10}
                stripedRows
                showGridlines
                removableSort
                size="small"
                loading={isLoading}
            >
                <Column field="quantity" header="Anzahl" sortable/>
                {(!type || type === InvoiceType.HP) &&
                    <Column field="number" header="Ziffer" sortable/>
                }
                <Column field="description" header="Beschreibung" sortable/>
                <Column field="amount" header="Einzelpreis" sortable/>
                <Column header="Einfügeposition" sortable body={positionToGerman}/>
                {!type &&
                    <Column field="type" header="Rechnungstyp" sortable/>
                }
                <Column field="is_active_global" header="Aktiv (Global)" body={activeTemplate}/>
            </DataTable>
        </div>
    )
}