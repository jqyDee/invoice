import React, { useState } from 'react';
import { Header } from '../utilities/header.tsx';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { PrivacyClauseForm } from './settings/privacy-clause-form.tsx';
import { PrivacyClauseTable } from './settings/privacy-clause-table.tsx';


export const SettingsPrivacyClausesView: React.FC = () => {
    const [visible, setVisible] = useState(false);

    return (
        <div className="flex-column">
            <div className="flex justify-content-between align-items-center">
                <Header title="Datenschutz-Klauseln" />
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
                style={{ maxWidth: '80vw' }}
                onHide={() => setVisible(false)}
            >
                <PrivacyClauseForm onSuccess={() => setVisible(false)} />
            </Dialog>

            <PrivacyClauseTable />
        </div>
    );
};
