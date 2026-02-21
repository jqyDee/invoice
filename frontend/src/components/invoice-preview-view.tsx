import React from "react";
import {client} from "../api/client.gen.ts";
import {useParams} from "react-router-dom";

export const InvoicePreviewView: React.FC = () => {
    const { id } = useParams();
    const baseUrl = client.getConfig().baseUrl;
    const directUrl = `${baseUrl}/pdf/${id}`;

    return (
        <div className="flex flex-column" style={{ height: 'calc(100vh - 70px)' }}>
            <iframe
                src={directUrl} // Point directly to the API, not a Blob URL
                className="flex-grow-1 border-none w-full"
                title="Invoice Preview"
            />
        </div>
    );
};