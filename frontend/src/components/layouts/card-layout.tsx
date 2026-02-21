import React from 'react';
import { Outlet } from 'react-router-dom';
import { Card } from "primereact/card";

export const CardLayout: React.FC = () => {
    return (
        <div className="flex justify-content-center">
            <Card className="card m-4 col-9">
                <Outlet />
            </Card>
        </div>
    );
};