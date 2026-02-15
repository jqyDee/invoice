/**
 * This code is part of the skeleton project provided for students of the course "Software
 * Architecture" offered by Innsbruck University.
 */
import React from 'react';
import {Menubar} from "primereact/menubar";
import {menu} from "../config/menu.ts";

/**
 * Navbar component.
 */
export const Navbar: React.FC = () => {
    return (
        <Menubar model={menu} className="gap-2"/>
    );
}
