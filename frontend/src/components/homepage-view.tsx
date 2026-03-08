import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getInvoicesInvoicesGetOptions } from "../api/@tanstack/react-query.gen.ts";
import { InvoiceTable } from './invoice/invoice-table.tsx';
import {Header} from "../utilities/header.tsx";

export const HomepageView: React.FC = () => {
    const { data: openInvoices, isLoading: openInvoicesLoading} = useQuery({
        ...getInvoicesInvoicesGetOptions({
            query: { only_open: true}
        })
    });

    return (
        <div className="flex flex-column gap-2">
            <Header title="Testing" />
            <Header title="Offene Rechnungen"/>
            <InvoiceTable invoices={openInvoices} isLoading={openInvoicesLoading} />
        </div>
    );
};