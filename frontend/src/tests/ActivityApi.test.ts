import { afterEach, describe, expect, it, vi } from 'vitest';
import { activityAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('activity API contract', () => {
    it('encodes AI-system and source filters', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } }));
        await activityAPI.list('activity-token', { aiSystemId: 3, sourceType: 'finding' });
        expect(fetchMock.mock.calls[0][0]).toBe('/api/activity?ai_system_id=3&source_type=finding');
        expect((fetchMock.mock.calls[0][1]?.headers as Headers).get('Authorization')).toBe('Bearer activity-token');
    });
});
