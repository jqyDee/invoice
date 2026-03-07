import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    deletePrivacyClauseEndpointPrivacyClausesClauseIdDeleteMutation,
    getPrivacyClausesPrivacyClausesGetOptions,
    getPrivacyClausesPrivacyClausesGetQueryKey,
} from '../../api/@tanstack/react-query.gen';
import { type PrivacyClause } from '../../api';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { PrivacyClauseForm } from './privacy-clause-form.tsx';
import { useGlobalToast } from '../../hooks/use-global-toast.ts';


export const PrivacyClauseTable: React.FC = () => {
    const queryClient = useQueryClient();
    const { showToast } = useGlobalToast();
    const [editClause, setEditClause] = useState<PrivacyClause | null>(null);

    const { data: clauses, isLoading } = useQuery({
        ...getPrivacyClausesPrivacyClausesGetOptions(),
        retry: false,
    });

    const deleteMutation = useMutation({
        ...deletePrivacyClauseEndpointPrivacyClausesClauseIdDeleteMutation(),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: getPrivacyClausesPrivacyClausesGetQueryKey() });
            showToast({ severity: 'success', summary: 'Erfolg', detail: 'Klausel gelöscht' });
        },
    });

    const actionsTemplate = (rowData: PrivacyClause) => (
        <div className="flex gap-2 justify-content-end">
            <Button
                icon="pi pi-pencil"
                className="p-button-rounded"
                onClick={() => setEditClause(rowData)}
            />
            <Button
                icon="pi pi-trash"
                className="p-button-danger p-button-rounded"
                loading={deleteMutation.isPending}
                onClick={() => deleteMutation.mutate({ path: { clause_id: rowData.clause_id } })}
            />
        </div>
    );

    return (
        <div>
            <Dialog
                header="Klausel bearbeiten"
                visible={editClause !== null}
                style={{ minWidth: '50vw' }}
                onHide={() => setEditClause(null)}
            >
                {editClause && (
                    <PrivacyClauseForm existing={editClause} onSuccess={() => setEditClause(null)} />
                )}
            </Dialog>

            <DataTable
                value={clauses}
                paginator
                rows={20}
                stripedRows
                showGridlines
                removableSort
                size="small"
                loading={isLoading}
                sortField="number"
                sortOrder={1}
            >
                <Column field="number" header="Nr." sortable style={{ width: '4rem' }} />
                <Column field="title" header="Titel" sortable />
                <Column field="description" header="Beschreibung" />
                <Column field="is_preamble" header="Präambel" body={(row: PrivacyClause) => row.is_preamble ? 'Ja' : 'Nein'} style={{ width: '6rem' }} />
                <Column header="" body={actionsTemplate} style={{ width: '7rem' }} />
            </DataTable>
        </div>
    );
};
