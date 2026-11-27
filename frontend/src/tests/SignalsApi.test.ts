import { afterEach, describe, expect, it, vi } from 'vitest';
import { signalsAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('operational signals API contract', () => {
    it('sends a signal with operational response metadata', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ id: 8 }), { status: 201, headers: { 'Content-Type': 'application/json' } }));
        await signalsAPI.create('signal-token', {
            ai_system_id: 3,
            finding_id: 7,
            review_id: undefined,
            signal_type: 'incident',
            severity: 'high',
            status: 'new',
            title: 'Unexpected answer pattern',
            description: 'A user reported an unexpected answer.',
            reported_by: 'Support team',
            reported_on: '2027-04-05',
            owner: 'AI operations',
            response_action: 'Review examples.',
            reviewer_notes: 'Human follow-up required.',
        });
        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toBe('/api/signals');
        expect((options?.headers as Headers).get('Authorization')).toBe('Bearer signal-token');
        expect(JSON.parse(String(options?.body))).toMatchObject({ ai_system_id: 3, finding_id: 7, signal_type: 'incident', severity: 'high' });
    });

    it('encodes system, type, severity, and status filters', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } }));
        await signalsAPI.list('signal-token', { aiSystemId: 3, signalType: 'feedback', severity: 'medium', status: 'triaged' });
        expect(fetchMock.mock.calls[0][0]).toBe('/api/signals?ai_system_id=3&signal_type=feedback&severity=medium&status=triaged');
    });
});
