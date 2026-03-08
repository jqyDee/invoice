import React from "react";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";

interface UnsavedChangesDialogProps {
    visible: boolean;
    onHide: () => void;
    onLeave: () => void;
    onSaveDraft: () => Promise<void>;
}

export const UnsavedChangesDialog: React.FC<UnsavedChangesDialogProps> = ({
    visible,
    onHide,
    onLeave,
    onSaveDraft,
}) => {
    return (
        <Dialog
            visible={visible}
            onHide={onHide}
            header="Ungespeicherte Änderungen"
            style={{ maxWidth: "80vw" }}
            footer={
                <div className="flex flex-column md:flex-row justify-content-between gap-2">
                    <Button
                        label="Abbrechen"
                        className="p-button-text"
                        onClick={onHide}
                    />
                    <div className="flex flex-column md:flex-row gap-2">
                        <Button
                            label="Verlassen"
                            className="p-button-outlined p-button-danger"
                            onClick={onLeave}
                        />
                        <Button
                            label="Entwurf speichern"
                            icon="pi pi-save"
                            onClick={onSaveDraft}
                        />
                    </div>
                </div>
            }
        >
            <p>Sie haben ungespeicherte Änderungen. Möchten Sie die Rechnung als Entwurf speichern, bevor Sie die Seite verlassen?</p>
        </Dialog>
    );
};
