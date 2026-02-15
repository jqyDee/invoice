import React from "react";

interface HeaderProps {
    title: string;
}

export const Header: React.FC<HeaderProps> = ({ title }) => {
    return (
        <h2 className="text-3xl mb-3">{title}</h2>
    )
}