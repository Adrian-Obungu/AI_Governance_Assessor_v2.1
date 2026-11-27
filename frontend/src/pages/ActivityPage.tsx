import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { activityAPI, inventoryAPI } from '../services/api';
import { ApiError } from '../services/apiErrors';
import type { ActivityEvent, ActivitySource, AISystem } from '../types';

const sourceLabels: Record<ActivitySource, string> = {
    inventory: 'Inventory', assessment: 'Assessment', evidence: 'Evidence', finding: 'Finding', review: 'Human review', signal: 'Signal',
};

const ActivityPage: React.FC = () => {
    const { token, expireSession } = useAuth();
    const [systems, setSystems] = useState<AISystem[]>([]);
    const [events, setEvents] = useState<ActivityEvent[]>([]);
    const [systemFilter, setSystemFilter] = useState('');
    const [sourceFilter, setSourceFilter] = useState<ActivitySource | ''>('');
    const [error, setError] = useState('');

    const load = useCallback(async () => {
        if (!token) return;
        try {
            setError('');
            setEvents(await activityAPI.list(token, { aiSystemId: systemFilter ? Number(systemFilter) : undefined, sourceType: sourceFilter || undefined }));
        } catch (err) {
            if (err instanceof ApiError && err.kind === 'unauthorized') { expireSession(); return; }
            setError(err instanceof ApiError ? err.message : 'We could not load the governance activity.');
        }
    }, [token, systemFilter, sourceFilter, expireSession]);

    useEffect(() => {
        if (!token) return;
        inventoryAPI.list(token).then(setSystems).catch(() => setError('We could not load your AI-system inventory.'));
    }, [token]);
    useEffect(() => {
        const timer = window.setTimeout(() => { void load(); }, 0);
        return () => window.clearTimeout(timer);
    }, [load]);

    return <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm"><div className="max-w-5xl mx-auto px-4 py-4"><h1 className="text-2xl font-bold text-gray-800">Governance activity</h1><p className="text-sm text-gray-600">A single view of the governance work already recorded for your AI systems.</p></div></nav>
        <main className="max-w-5xl mx-auto px-4 py-8">
            <section className="card mb-6 border-l-4 border-primary-500"><p className="text-sm text-gray-700">This is a derived, read-only timeline. Use the linked workspaces to change evidence, findings, reviews, or signals. It does not determine legal status, certification, or objective safety.</p></section>
            <section className="card mb-6 flex flex-col gap-3 sm:flex-row sm:items-end"><label className="text-sm text-gray-700">AI system<select className="input-field mt-1" value={systemFilter} onChange={e => setSystemFilter(e.target.value)}><option value="">All systems</option>{systems.map(system => <option key={system.id} value={system.id}>{system.name}</option>)}</select></label><label className="text-sm text-gray-700">Activity type<select className="input-field mt-1" value={sourceFilter} onChange={e => setSourceFilter(e.target.value as ActivitySource | '')}><option value="">All activity</option>{(Object.keys(sourceLabels) as ActivitySource[]).map(source => <option key={source} value={source}>{sourceLabels[source]}</option>)}</select></label></section>
            {error && <div role="alert" className="card mb-6 border border-red-200 bg-red-50 text-red-700">{error}</div>}
            {events.length === 0 ? <div className="card text-center text-gray-600">No recorded activity matches these filters.</div> : <div className="relative space-y-4 before:absolute before:bottom-4 before:left-5 before:top-4 before:w-px before:bg-primary-200">{events.map(event => <article className="card relative ml-2 pl-12" key={`${event.source_type}-${event.source_id}`}><span className="absolute left-3 top-6 h-4 w-4 rounded-full border-4 border-primary-100 bg-primary-600" aria-hidden="true" /><div className="flex flex-wrap items-start justify-between gap-3"><div><span className="rounded bg-primary-50 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-primary-700">{sourceLabels[event.source_type]}</span><h2 className="mt-2 text-lg font-bold text-gray-800">{event.title}</h2></div><time className="text-sm text-gray-500" dateTime={event.occurred_at}>{new Date(event.occurred_at).toLocaleDateString()}</time></div><p className="mt-2 text-gray-700">{event.summary}</p><div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-600">{event.status && <span className="rounded bg-gray-100 px-2 py-1">Status: {event.status.replace('_', ' ')}</span>}{event.priority && <span className="rounded bg-amber-100 px-2 py-1 text-amber-800">Priority: {event.priority}</span>}{event.severity && <span className="rounded bg-orange-100 px-2 py-1 text-orange-800">Severity: {event.severity}</span>}</div></article>)}</div>}
        </main>
    </div>;
};
export default ActivityPage;
