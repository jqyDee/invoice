import React, {useState} from "react";
import {Header} from "../utilities/header.tsx";
import {DefaultItemTable} from "./settings/default-item-table.tsx";
import {Button} from "primereact/button";
import {Dialog} from "primereact/dialog";
import {DefaultItemForm} from "./settings/default-item-form.tsx";


export const SettingsDefaultsView: React.FC = () => {
    const [visible, setVisible] = useState<boolean>(false);

    const openEdit = () => {
        setVisible(true);
    }

    return (
        <div className="flex-column">
            <div className="flex justify-content-between align-items-center">
                <Header title="Voreinstellungen" />
                <Button className="p-button-rounded" label="Neue Voreinstellung" icon="pi pi-plus" onClick={openEdit}/>
            </div>

            <Dialog
                header="Voreinstellung erstellen"
                visible={visible}
                style={{ maxWidth: '50vw' }}
                onHide={() => setVisible(false)}
            >
                <DefaultItemForm onSuccess={() => setVisible(false)} />
            </Dialog>

            <DefaultItemTable />
        </div>
    )
}