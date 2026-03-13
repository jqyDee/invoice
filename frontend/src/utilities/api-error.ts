import type { HttpValidationError } from '../api/types.gen.ts'

export function extractApiError(error: HttpValidationError | unknown): string {
    if (error && typeof error === 'object' && 'detail' in error) {
        const detail = (error as { detail: unknown }).detail
        if (typeof detail === 'string') return detail
        if (Array.isArray(detail)) {
            return detail.map((e) => (typeof e === 'object' && e !== null && 'msg' in e ? e.msg : String(e))).join(', ')
        }
    }
    return 'Ein unbekannter Fehler ist aufgetreten.'
}
