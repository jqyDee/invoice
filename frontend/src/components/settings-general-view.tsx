import React from "react";
import {Header} from "../utilities/header.tsx";
import {GeneralForm} from "./settings/general-form.tsx";


export const SettingsGeneralView: React.FC = () => {
    return (
        <div className="flex-column">
            <Header title="Einstellungen" />
            <GeneralForm />
        </div>
    )
}