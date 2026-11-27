import { afterEach, describe, expect, it, vi } from 'vitest';
import { assessmentAPI, inventoryAPI } from '../services/api';

afterEach(() => vi.restoreAllMocks());

describe('inventory API contract', () => {
    it('attaches the bearer token and sends the guided intake payload', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
            new Response(JSON.stringify({
                id: 1,
                user_id: 7,
                name: 'Support assistant',
                purpose: 'Answer support questions',
                lifecycle_stage: 'pilot',
                geographies: ['Kenya'],
                data_categories: [],
                affected_groups: [],
                created_at: '2026-11-27T00:00:00Z',
                updated_at: '2026-11-27T00:00:00Z',
            }), { status: 201, headers: { 'Content-Type': 'application/json' } }),
        );

        await inventoryAPI.create('test-token', {
            name: 'Support assistant',
            purpose: 'Answer support questions',
            lifecycle_stage: 'pilot',
            geographies: ['Kenya'],
            data_categories: [],
            affected_groups: [],
        });

        expect(fetchMock).toHaveBeenCalledTimes(1);
        const [url, options] = fetchMock.mock.calls[0];
        expect(url).toBe('/api/inventory');
        expect((options?.headers as Headers).get('Authorization')).toBe('Bearer test-token');
        expect(JSON.parse(String(options?.body))).toMatchObject({
            name: 'Support assistant',
            lifecycle_stage: 'pilot',
            geographies: ['Kenya'],
        });
    });

    it('sends an optional inventory context when creating an assessment', async () => {
        const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
            new Response(JSON.stringify({ id: 3 }), { status: 201, headers: { 'Content-Type': 'application/json' } }),
        );

        await assessmentAPI.createAssessment('test-token', 'Context review', 'Review description', 12);

        const [, options] = fetchMock.mock.calls[0];
        expect(JSON.parse(String(options?.body))).toMatchObject({
            title: 'Context review',
            ai_system_id: 12,
        });
    });
});
