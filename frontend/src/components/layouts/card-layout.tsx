import React from 'react';
import {Outlet} from 'react-router-dom';
import {Card} from "primereact/card";

export const CardLayout: React.FC = () => {
    return (
        <div className="flex justify-content-center">
            <Card className="col-12 m-0 shadow-none border-none md:col-9 md:m-4 md:shadow-2">
                <Outlet/>
            </Card>
        </div>
    );
};