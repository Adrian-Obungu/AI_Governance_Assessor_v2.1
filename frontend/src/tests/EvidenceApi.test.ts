import { afterEach, describe, expect, it, vi } from 'vitest';
import { evidenceAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('evidence API contract', () => {
    it('sends metadata-only evidence with context and bearer token', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ id: 9 }), { status: 201, headers: { 'Content-Type': 'application/json' } }));
        await evidenceAPI.create('evidence-token', { ai_system_id: 4, assessment_id: 12, title: 'Data policy', description: 'Covers customer data handling.', evidence_type: 'policy', status: 'submitted' });
        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toBe('/api/evidence');
        expect((options?.headers as Headers).get('Authorization')).toBe('Bearer evidence-token');
        expect(JSON.parse(String(options?.body))).toMatchObject({ ai_system_id: 4, assessment_id: 12, evidence_type: 'policy', status: 'submitted' });
    });

    it('encodes system and status filters in the list request', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } }));
        await evidenceAPI.list('evidence-token', { aiSystemId: 4, status: 'needs_update' });
        expect(fetchMock.mock.calls[0][0]).toBe('/api/evidence?ai_system_id=4&status=needs_update');
    });
});
