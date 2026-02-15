import {defineConfig} from '@hey-api/openapi-ts';

export default defineConfig({
    input: 'http://localhost:8000/openapi.json',
    output: 'src/api',
    parser: {
        transforms: {
            enums: 'root',
        },
    },
    plugins: [
        {
            name: '@hey-api/typescript',
            enums: 'javascript',
        },
        '@hey-api/sdk',
        '@tanstack/react-query'
    ],
});