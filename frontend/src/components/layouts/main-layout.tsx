import React from 'react';
import {Outlet} from 'react-router-dom';
import {NavbarView} from "../navbar-view.tsx";

export const MainLayout: React.FC = () => {
    return (
        <div className="main-layout">
            <NavbarView/>
            <main>
                <Outlet/>
            </main>
        </div>
    );
};