import React, { useState } from 'react';
import { Header } from '../utilities/header.tsx';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { TherapyClauseForm } from './settings/therapy-clause-form.tsx';
import { TherapyClauseTable } from './settings/therapy-clause-table.tsx';


export const SettingsTherapyClausesView: React.FC = () => {
    const [visible, setVisible] = useState(false);

    return (
        <div className="flex-column">
            <div className="flex justify-content-between align-items-center">
                <Header title="Therapie-Klauseln" />
                <Button
                    className="p-button-rounded"
                    label="Neue Klausel"
                    icon="pi pi-plus"
                    onClick={() => setVisible(true)}
                />
            </div>

            <Dialog
                header="Klausel erstellen"
                visible={visible}
                style={{ minWidth: '50vw' }}
                onHide={() => setVisible(false)}
            >
                <TherapyClauseForm onSuccess={() => setVisible(false)} />
            </Dialog>

            <TherapyClauseTable />
        </div>
    );
};
