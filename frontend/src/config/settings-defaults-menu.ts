import type {MenuItem} from "primereact/menuitem";
import {generatePath, useNavigate} from "react-router-dom";
import {ROUTES} from "./routes.ts";


export const useSettingsDefaultsMenu = (): MenuItem[] => {
    const navigate = useNavigate()

    return [
        {
            label: 'Alle',
            icon: 'pi pi-home',
            command: () => navigate(generatePath(ROUTES.SETTINGS_DEFAULTS, {type: ''}))
        },
        {
            label: 'Krankengymnastik',
            icon: 'pi pi-home',
            command: () => navigate(generatePath(ROUTES.SETTINGS_DEFAULTS, {type: 'KG'}))
        },
        {
            label: 'Heilpraktiker',
            icon: 'pi pi-chart-line',
            command: () => navigate(generatePath(ROUTES.SETTINGS_DEFAULTS, {type: 'HP'}))
        },
        {
            label: 'Gestalttherapie',
            icon: 'pi pi-chart-line',
            command: () => navigate(generatePath(ROUTES.SETTINGS_DEFAULTS, {type: 'GT'}))
        },
    ]
};
