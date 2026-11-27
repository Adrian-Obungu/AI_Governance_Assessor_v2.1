import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { inventoryAPI, snapshotAPI } from '../services/api';
import { ApiError } from '../services/apiErrors';
import type { AISystem, GovernanceSnapshot } from '../types';

const SnapshotPage: React.FC = () => {
    const { token, expireSession } = useAuth();
    const navigate = useNavigate();
    const [systems, setSystems] = useState<AISystem[]>([]);
    const [selectedSystem, setSelectedSystem] = useState('');
    const [snapshot, setSnapshot] = useState<GovernanceSnapshot | null>(null);
    const [error, setError] = useState('');

    const load = useCallback(async () => {
        if (!token || !selectedSystem) return;
        try {
            setError('');
            const snapshots = await snapshotAPI.list(token, Number(selectedSystem));
            setSnapshot(snapshots[0] ?? null);
        } catch (err) {
            if (err instanceof ApiError && err.kind === 'unauthorized') { expireSession(); return; }
            setError(err instanceof ApiError ? err.message : 'We could not load this governance snapshot.');
        }
    }, [token, selectedSystem, expireSession]);

    useEffect(() => {
        if (!token) return;
        inventoryAPI.list(token).then(items => {
            setSystems(items);
            if (items.length > 0) setSelectedSystem(String(items[0].id));
        }).catch(() => setError('We could not load your AI-system inventory.'));
    }, [token]);
    useEffect(() => {
        const timer = window.setTimeout(() => { void load(); }, 0);
        return () => window.clearTimeout(timer);
    }, [load]);

    const goToSource = (source: string) => {
        const routes: Record<string, string> = { inventory: '/inventory', assessment: '/dashboard', evidence: '/evidence', finding: '/findings', review: '/reviews', signal: '/signals' };
        navigate(routes[source] ?? '/dashboard');
    };

    return <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm"><div className="max-w-6xl mx-auto px-4 py-4"><h1 className="text-2xl font-bold text-gray-800">AI-system governance snapshot</h1><p className="text-sm text-gray-600">A concise view of recorded workflow coverage and human follow-up prompts.</p></div></nav>
        <main className="max-w-6xl mx-auto px-4 py-8">
            <section className="card mb-6 border-l-4 border-primary-500"><p className="text-sm text-gray-700">This snapshot reflects records your team has entered. It is not a risk score, legal conclusion, certification, or objective safety determination.</p></section>
            <section className="card mb-6"><label className="block max-w-xl text-sm font-medium text-gray-700">AI system<select className="input-field mt-1" value={selectedSystem} onChange={e => setSelectedSystem(e.target.value)}><option value="">Choose a system</option>{systems.map(system => <option key={system.id} value={system.id}>{system.name}</option>)}</select></label></section>
            {error && <div role="alert" className="card mb-6 border border-red-200 bg-red-50 text-red-700">{error}</div>}
            {!snapshot && !error && <div className="card text-center text-gray-600">Select an AI system to view its governance snapshot.</div>}
            {snapshot && <><section className="card mb-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm font-semibold uppercase tracking-wide text-primary-600">{snapshot.lifecycle_stage.replace('_', ' ')}</p><h2 className="mt-1 text-2xl font-bold text-gray-800">{snapshot.system_name}</h2></div><div className={`rounded px-3 py-2 text-sm font-semibold ${snapshot.review_due ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>{snapshot.review_due ? 'Review date reached' : 'No review-date prompt'}</div></div>{snapshot.review_date && <p className="mt-3 text-sm text-gray-600">Review date: {snapshot.review_date}</p>}<div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">{[['Assessments', snapshot.coverage.assessments], ['Evidence', snapshot.coverage.evidence_records], ['Findings', snapshot.coverage.findings], ['Human reviews', snapshot.coverage.human_reviews], ['Signals', snapshot.coverage.operational_signals], ['Open findings', snapshot.open_findings]].map(([label, value]) => <div className="rounded border border-gray-200 bg-gray-50 p-3" key={String(label)}><p className="text-xs text-gray-500">{label}</p><p className="mt-1 text-2xl font-bold text-gray-800">{value}</p></div>)}</div></section><section className="card mb-6 border-l-4 border-amber-400"><p className="text-sm font-semibold uppercase tracking-wide text-amber-700">Next human action</p><p className="mt-2 text-lg font-semibold text-gray-800">{snapshot.next_action}</p></section><section><h2 className="mb-3 text-xl font-bold text-gray-800">Attention items</h2><div className="space-y-3">{snapshot.attention.map((item, index) => <article className={`card flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between ${item.level === 'attention' ? 'border-l-4 border-amber-400' : 'border-l-4 border-emerald-400'}`} key={`${item.source_type}-${item.source_id ?? index}`}><div><h3 className="font-semibold text-gray-800">{item.title}</h3><p className="mt-1 text-sm text-gray-600">{item.detail}</p></div><button className="btn-secondary whitespace-nowrap" onClick={() => goToSource(item.source_type)}>Open {item.source_type.replace('_', ' ')}</button></article>)}</div></section></>}
        </main>
    </div>;
};
export default SnapshotPage;
