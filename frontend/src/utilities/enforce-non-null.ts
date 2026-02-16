import type {Nullable} from "primereact/ts-helpers";

export function enforceNonNull<T>(value: Nullable<T>): NonNullable<T> {
    if (value === null || value === undefined) {
        throw new Error("EnforceNonNull value: " + value);
    }
    return value;
}