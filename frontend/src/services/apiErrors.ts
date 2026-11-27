export type ApiErrorKind =
    | 'unauthorized'
    | 'forbidden'
    | 'not_found'
    | 'validation'
    | 'conflict'
    | 'rate_limited'
    | 'server'
    | 'network'
    | 'aborted'
    | 'unknown';

export class ApiError extends Error {
    readonly kind: ApiErrorKind;
    readonly status?: number;
    readonly detail?: string;
    readonly retryable: boolean;

    constructor(
        message: string,
        options: {
            kind: ApiErrorKind;
            status?: number;
            detail?: string;
            retryable?: boolean;
        },
    ) {
        super(message);
        this.name = 'ApiError';
        this.kind = options.kind;
        this.status = options.status;
        this.detail = options.detail;
        this.retryable = options.retryable ?? false;
    }
}

export function classifyHttpStatus(status: number, detail?: string): ApiError {
    const mapping: Record<number, { kind: ApiErrorKind; retryable: boolean; message: string }> = {
        401: { kind: 'unauthorized', retryable: false, message: 'Your session expired. Please sign in again.' },
        403: { kind: 'forbidden', retryable: false, message: 'You do not have access to this resource.' },
        404: { kind: 'not_found', retryable: false, message: 'The requested resource could not be found.' },
        409: { kind: 'conflict', retryable: false, message: 'This resource changed. Please reload and try again.' },
        422: { kind: 'validation', retryable: false, message: 'Please check the submitted values and try again.' },
        429: { kind: 'rate_limited', retryable: true, message: 'Too many requests. Please try again shortly.' },
    };
    const mapped = mapping[status];
    if (mapped) {
        return new ApiError(detail || mapped.message, { ...mapped, status, detail });
    }
    if (status >= 500) {
        return new ApiError('The service is temporarily unavailable. Please try again.', {
            kind: 'server',
            status,
            detail,
            retryable: true,
        });
    }
    return new ApiError(detail || 'The request could not be completed.', {
        kind: 'unknown',
        status,
        detail,
    });
}

export function classifyRequestFailure(error: unknown): ApiError {
    if (error instanceof ApiError) return error;
    if (error instanceof DOMException && error.name === 'AbortError') {
        return new ApiError('The request was cancelled.', { kind: 'aborted' });
    }
    if (error instanceof TypeError) {
        return new ApiError('We could not reach the service. Check your connection and try again.', {
            kind: 'network',
            retryable: true,
        });
    }
    return new ApiError('An unexpected error occurred. Please try again.', { kind: 'unknown' });
}
