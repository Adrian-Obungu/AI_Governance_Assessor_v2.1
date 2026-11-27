import { afterEach, describe, expect, it, vi } from 'vitest';
import { snapshotAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('governance snapshot API contract', () => {
    it('requests one AI-system snapshot with ownership token', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } }));
        await snapshotAPI.list('snapshot-token', 9);
        expect(fetchMock.mock.calls[0][0]).toBe('/api/governance/snapshots?ai_system_id=9');
        expect((fetchMock.mock.calls[0][1]?.headers as Headers).get('Authorization')).toBe('Bearer snapshot-token');
    });
});
