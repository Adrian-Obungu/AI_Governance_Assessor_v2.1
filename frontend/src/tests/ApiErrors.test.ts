import { describe, expect, it } from 'vitest';
import {
    ApiError,
    classifyHttpStatus,
    classifyRequestFailure,
} from '../services/apiErrors';

describe('Phase 4 API error taxonomy', () => {
    it.each([
        [401, 'unauthorized', false],
        [403, 'forbidden', false],
        [404, 'not_found', false],
        [409, 'conflict', false],
        [422, 'validation', false],
        [429, 'rate_limited', true],
        [500, 'server', true],
    ] as const)('maps HTTP %s to %s with retry=%s', (status, kind, retryable) => {
        const error = classifyHttpStatus(status);
        expect(error).toBeInstanceOf(ApiError);
        expect(error.kind).toBe(kind);
        expect(error.retryable).toBe(retryable);
        expect(error.status).toBe(status);
    });

    it('preserves structured server detail when provided', () => {
        const error = classifyHttpStatus(422, 'invalid_answers');
        expect(error.detail).toBe('invalid_answers');
        expect(error.message).toBe('invalid_answers');
    });

    it('classifies network failures as retryable', () => {
        const error = classifyRequestFailure(new TypeError('Failed to fetch'));
        expect(error.kind).toBe('network');
        expect(error.retryable).toBe(true);
    });

    it('does not make an intentional abort retryable', () => {
        const error = classifyRequestFailure(new DOMException('cancelled', 'AbortError'));
        expect(error.kind).toBe('aborted');
        expect(error.retryable).toBe(false);
    });

    it('does not wrap an existing ApiError', () => {
        const original = classifyHttpStatus(401);
        expect(classifyRequestFailure(original)).toBe(original);
    });
});
