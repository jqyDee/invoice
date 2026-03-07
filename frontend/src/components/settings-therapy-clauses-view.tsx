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
            <div className="flex flex-column md:flex-row justify-content-between md:align-items-center gap-3 mb-3">
                <Header title="Therapie-Klauseln" />

                <div className="flex gap-2 w-full md:w-auto">
                    <Button
                        className="p-button-rounded w-full md:w-auto"
                        label="Neue Klausel"
                        icon="pi pi-plus"
                        onClick={() => setVisible(true)}
                    />
                </div>
            </div>

            <Dialog
                header="Klausel erstellen"
                visible={visible}
                style={{ maxWidth: '80vw' }}
                onHide={() => setVisible(false)}
            >
                <TherapyClauseForm onSuccess={() => setVisible(false)} />
            </Dialog>

            <TherapyClauseTable />
        </div>
    );
};
