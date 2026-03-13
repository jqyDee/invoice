/**
 * This code is part of the skeleton project provided for students of the course "Software
 * Architecture" offered by Innsbruck University.
 */
import React from 'react';
import {Menubar} from "primereact/menubar";
import {useNavigate} from "react-router-dom";
import {buildMenu} from "../config/menu.ts";
import {Button} from "primereact/button";
import {useAuth} from "../contexts/auth-context.tsx";
import {useIsMobile} from "../hooks/use-is-mobile.ts";

/**
 * NavbarView component.
 */
export const NavbarView: React.FC = () => {
    const navigate = useNavigate();
    const isMobile = useIsMobile();
    const {logout} = useAuth();
    const end = <Button icon="pi pi-sign-out" label={isMobile ? '' : 'Abmelden'} text onClick={logout}/>;
    return (
        <Menubar model={buildMenu(navigate)} end={end} className="gap-4"/>
    );
}
