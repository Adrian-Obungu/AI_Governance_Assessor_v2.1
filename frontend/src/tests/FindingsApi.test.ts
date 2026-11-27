import { afterEach, describe, expect, it, vi } from 'vitest';
import { findingsAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('findings API contract', () => {
    it('sends a linked finding with remediation metadata', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ id: 4 }), { status: 201, headers: { 'Content-Type': 'application/json' } }));
        await findingsAPI.create('finding-token', { ai_system_id: 2, evidence_id: 8, title: 'Missing owner', conclusion: 'The review does not identify an accountable owner.', priority: 'high', owner: 'Operations', remediation_action: 'Assign a named owner.', status: 'open' });
        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toBe('/api/findings');
        expect((options?.headers as Headers).get('Authorization')).toBe('Bearer finding-token');
        expect(JSON.parse(String(options?.body))).toMatchObject({ ai_system_id: 2, evidence_id: 8, priority: 'high', remediation_action: 'Assign a named owner.' });
    });

    it('encodes system, status, and priority filters', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } }));
        await findingsAPI.list('finding-token', { aiSystemId: 2, status: 'in_progress', priority: 'critical' });
        expect(fetchMock.mock.calls[0][0]).toBe('/api/findings?ai_system_id=2&status=in_progress&priority=critical');
    });
});
