import React from "react";

interface TotalProps {
    total: number;
}

export const Total: React.FC<TotalProps> = ({total}) => {
    return (
        <div className="flex justify-content-end mt-2">
            <div className="flex flex-column align-items-end">
                <span className="font-light">TOTAL</span>
                <span className="font-bold">{total.toFixed(2)} €</span>
            </div>
        </div>
    )
}