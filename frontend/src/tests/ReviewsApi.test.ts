import { afterEach, describe, expect, it, vi } from 'vitest';
import { reviewsAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('reviews API contract', () => {
    it('sends a human review with material-change and reassessment metadata', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ id: 6 }), { status: 201, headers: { 'Content-Type': 'application/json' } }));
        await reviewsAPI.create('review-token', { ai_system_id: 3, assessment_id: 4, reassessment_id: 5, reviewer: 'Governance lead', review_date: '2027-03-31', decision: 'reassess', material_change: true, change_summary: 'Provider retention terms changed.' });
        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toBe('/api/reviews');
        expect((options?.headers as Headers).get('Authorization')).toBe('Bearer review-token');
        expect(JSON.parse(String(options?.body))).toMatchObject({ ai_system_id: 3, reassessment_id: 5, decision: 'reassess', material_change: true });
    });

    it('encodes system, decision, and material-change filters', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } }));
        await reviewsAPI.list('review-token', { aiSystemId: 3, decision: 'reassess', materialChange: true });
        expect(fetchMock.mock.calls[0][0]).toBe('/api/reviews?ai_system_id=3&decision=reassess&material_change=true');
    });
});
