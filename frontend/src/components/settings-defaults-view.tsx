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
            <div className="flex flex-column md:flex-row justify-content-between md:align-items-center gap-3 mb-3">
                <Header title="Voreinstellungen" />

                <div className="flex gap-2 w-full md:w-auto">
                    <Button className="p-button-rounded" label="Neue Voreinstellung" icon="pi pi-plus" onClick={openEdit}/>
                </div>
            </div>

            <Dialog
                header="Voreinstellung erstellen"
                visible={visible}
                style={{ maxWidth: '80vw' }}
                onHide={() => setVisible(false)}
            >
                <DefaultItemForm onSuccess={() => setVisible(false)} />
            </Dialog>

            <DefaultItemTable />
        </div>
    )
}