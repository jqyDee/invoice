import React from 'react';
import {useQuery} from '@tanstack/react-query';
import {getInvoicesInvoicesGetOptions} from "../api/@tanstack/react-query.gen.ts";
import {InvoiceTable} from './invoice/invoice-table.tsx';
import {Header} from "../utilities/header.tsx";

export const HomepageView: React.FC = () => {
    const [page, setPage] = React.useState(1);
    const [pageSize, setPageSize] = React.useState(20);
    const [sortField, setSortField] = React.useState("updated_at");
    const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("desc");

    const {data, isLoading: openInvoicesLoading} = useQuery({
        ...getInvoicesInvoicesGetOptions({
            query: {only_open: true, page, size: pageSize, sort_field: sortField, sort_order: sortOrder}
        })
    });

    return (
        <div className="flex flex-column gap-2">
            <Header title="Offene Rechnungen"/>
            <InvoiceTable
                invoices={data?.items}
                isLoading={openInvoicesLoading}
                totalRecords={data?.total ?? 0}
                page={page}
                pageSize={pageSize}
                onPageChange={(p, s) => { setPage(p); setPageSize(s); }}
                sortField={sortField}
                sortOrder={sortOrder}
                onSort={(f, o) => { setSortField(f); setSortOrder(o); setPage(1); }}
            />
        </div>
    );
};