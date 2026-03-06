import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    deleteTherapyClauseTherapyClausesClauseIdDeleteMutation,
    getTherapyClausesTherapyClausesGetOptions,
    getTherapyClausesTherapyClausesGetQueryKey,
} from '../../api/@tanstack/react-query.gen';
import { type TherapyClause } from '../../api';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { TherapyClauseForm } from './therapy-clause-form.tsx';
import { useGlobalToast } from '../../hooks/use-global-toast.ts';


export const TherapyClauseTable: React.FC = () => {
    const queryClient = useQueryClient();
    const { showToast } = useGlobalToast();
    const [editClause, setEditClause] = useState<TherapyClause | null>(null);

    const { data: clauses, isLoading } = useQuery({
        ...getTherapyClausesTherapyClausesGetOptions(),
        retry: false,
    });

    const deleteMutation = useMutation({
        ...deleteTherapyClauseTherapyClausesClauseIdDeleteMutation(),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: getTherapyClausesTherapyClausesGetQueryKey() });
            showToast({ severity: 'success', summary: 'Erfolg', detail: 'Klausel gelöscht' });
        },
    });

    const actionsTemplate = (rowData: TherapyClause) => (
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
                    <TherapyClauseForm existing={editClause} onSuccess={() => setEditClause(null)} />
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
                <Column header="" body={actionsTemplate} style={{ width: '7rem' }} />
            </DataTable>
        </div>
    );
};
