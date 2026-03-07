/**
 * This code is part of the skeleton project provided for students of the course "Software
 * Architecture" offered by Innsbruck University.
 */
import React from 'react';
import {Menubar} from "primereact/menubar";
import {useNavigate} from "react-router-dom";
import {buildMenu} from "../config/menu.ts";

/**
 * NavbarView component.
 */
export const NavbarView: React.FC = () => {
    const navigate = useNavigate();
    return (
        <Menubar model={buildMenu(navigate)} className="gap-4"/>
    );
}
