import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from "./navbar.tsx";

export const MainLayout: React.FC = () => {
    return (
        <div className="main-layout">
            <Navbar />
            <main>
                <Outlet />
            </main>
        </div>
    );
};