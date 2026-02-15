import React from "react";
import {Header} from "./header.tsx";
import {SettingsForm} from "./settings-form.tsx";


export const SettingsView: React.FC = () => {
    return (
        <div className="flex-column">
            <Header title="Einstellungen" />
            <SettingsForm />
        </div>
    )
}