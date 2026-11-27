import { ApiError, classifyHttpStatus, classifyRequestFailure } from './apiErrors';
import type { AISystem, Assessment, AssessmentResult, AssessmentSummary, Questionnaire } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

type ResponseType = 'json' | 'blob';

type RequestOptions = RequestInit & {
    token?: string;
    responseType?: ResponseType;
    timeoutMs?: number;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { token, responseType = 'json', timeoutMs = 15000, signal, headers, ...init } = options;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
    const abortListener = () => controller.abort();
    signal?.addEventListener('abort', abortListener, { once: true });

    const requestHeaders = new Headers(headers);
    if (token) requestHeaders.set('Authorization', `Bearer ${token}`);
    if (init.body && !requestHeaders.has('Content-Type')) requestHeaders.set('Content-Type', 'application/json');

    try {
        const response = await fetch(`${API_BASE_URL}${path}`, {
            ...init,
            headers: requestHeaders,
            signal: controller.signal,
        });

        if (!response.ok) {
            let detail: string | undefined;
            try {
                const payload = await response.json() as { detail?: unknown; message?: unknown };
                if (typeof payload.detail === 'string') detail = payload.detail;
                else if (typeof payload.message === 'string') detail = payload.message;
            } catch {
                // Some gateways return an HTML or empty error body.
            }
            throw classifyHttpStatus(response.status, detail);
        }

        if (responseType === 'blob') return await response.blob() as T;
        if (response.status === 204) return undefined as T;
        return await response.json() as T;
    } catch (error) {
        if (error instanceof ApiError) throw error;
        if (controller.signal.aborted && !signal?.aborted) {
            throw new ApiError('The request timed out. Please try again.', {
                kind: 'network',
                retryable: true,
            });
        }
        throw classifyRequestFailure(error);
    } finally {
        window.clearTimeout(timeout);
        signal?.removeEventListener('abort', abortListener);
    }
}

export const authAPI = {
    signup: (email: string, password: string, fullName?: string) => request<{ access_token: string }>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name: fullName }),
    }),
    login: (email: string, password: string) => request<{ access_token: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    }),
    requestPasswordReset: (email: string) => request('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
    }),
};

export const assessmentAPI = {
    getQuestionnaires: () => request<Questionnaire[]>('/assessments/questionnaires'),
    createAssessment: (token: string, title: string, description?: string) => request<Assessment>('/assessments', {
        method: 'POST', token, body: JSON.stringify({ title, description }),
    }),
    listAssessments: (token: string) => request<Assessment[]>('/assessments', { token }),
    getAssessment: (token: string, id: number) => request<Assessment>(`/assessments/${id}`, { token }),
    submitAnswers: (token: string, assessmentId: number, category: string, answers: Record<string, number>) => request<AssessmentResult>(`/assessments/${assessmentId}/answers`, {
        method: 'POST', token, body: JSON.stringify({ category, answers }),
        // Answer submissions are deliberately never retried automatically.
    }),
    getSummary: (token: string, assessmentId: number) => request<AssessmentSummary>(`/assessments/${assessmentId}/summary`, { token }),
    exportCSV: (token: string, assessmentId: number) => request<Blob>(`/assessments/${assessmentId}/export/csv`, { token, responseType: 'blob' }),
    exportPDF: (token: string, assessmentId: number) => request<Blob>(`/assessments/${assessmentId}/export/pdf`, { token, responseType: 'blob' }),
};

export const inventoryAPI = {
    list: (token: string) => request<AISystem[]>('/inventory', { token }),
    get: (token: string, id: number) => request<AISystem>(`/inventory/${id}`, { token }),
    create: (token: string, payload: Omit<AISystem, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => request<AISystem>('/inventory', {
        method: 'POST', token, body: JSON.stringify(payload),
    }),
    update: (token: string, id: number, payload: Partial<Omit<AISystem, 'id' | 'user_id' | 'created_at' | 'updated_at'>>) => request<AISystem>(`/inventory/${id}`, {
        method: 'PUT', token, body: JSON.stringify(payload),
    }),
};

export { request as apiRequest };
