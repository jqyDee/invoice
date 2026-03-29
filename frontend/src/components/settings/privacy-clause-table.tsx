import React, {useState} from 'react';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {
    deletePrivacyClauseEndpointPrivacyClausesClauseIdDeleteMutation,
    getPrivacyClausesPrivacyClausesGetOptions,
    getPrivacyClausesPrivacyClausesGetQueryKey,
} from '../../api/@tanstack/react-query.gen';
import {type PrivacyClause} from '../../api';
import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {Button} from 'primereact/button';
import {Dialog} from 'primereact/dialog';
import {PrivacyClauseForm} from './privacy-clause-form.tsx';
import {useGlobalToast} from '../../hooks/use-global-toast.ts';
import {useIsMobile} from '../../hooks/use-is-mobile.ts';


export const PrivacyClauseTable: React.FC = () => {
    const queryClient = useQueryClient();
    const {showToast} = useGlobalToast();
    const isMobile = useIsMobile();
    const [editClause, setEditClause] = useState<PrivacyClause | null>(null);

    const {data: clauses, isLoading} = useQuery({
        ...getPrivacyClausesPrivacyClausesGetOptions(),
        retry: false,
    });

    const deleteMutation = useMutation({
        ...deletePrivacyClauseEndpointPrivacyClausesClauseIdDeleteMutation(),
        onSuccess: async () => {
            await queryClient.invalidateQueries({queryKey: getPrivacyClausesPrivacyClausesGetQueryKey()});
            showToast({severity: 'success', summary: 'Erfolg', detail: 'Klausel gelöscht'});
        },
    });

    const actionsTemplate = (rowData: PrivacyClause) => (
        <div className="flex flex-column md:flex-row gap-2 justify-content-end align-items-end">
            <div className="flex gap-2">
                <Button
                    icon="pi pi-pencil"
                    className="p-button-rounded"
                    onClick={() => setEditClause(rowData)}
                />
            </div>
            <div className="flex gap-2">
                <Button
                    icon="pi pi-trash"
                    className="p-button-danger p-button-rounded"
                    loading={deleteMutation.isPending}
                    onClick={() => deleteMutation.mutate({path: {clause_id: rowData.clause_id}})}
                />
            </div>
        </div>
    );

    return (
        <div>
            <Dialog
                header="Klausel bearbeiten"
                visible={editClause !== null}
                style={{minWidth: '50vw'}}
                onHide={() => setEditClause(null)}
            >
                {editClause && (
                    <PrivacyClauseForm existing={editClause} onSuccess={() => setEditClause(null)}/>
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
                {!isMobile && <Column field="number" header="Nr." sortable style={{width: '4rem'}}/>}
                {!isMobile && <Column field="title" header="Titel" sortable/>}
                <Column field="description" header="Beschreibung"/>
                {!isMobile && <Column field="is_preamble" header="Präambel"
                                      body={(row: PrivacyClause) => row.is_preamble ? 'Ja' : 'Nein'}
                                      style={{width: '6rem'}}/>}
                <Column header="" body={actionsTemplate} className="white-space-nowrap"/>
            </DataTable>
        </div>
    );
};
