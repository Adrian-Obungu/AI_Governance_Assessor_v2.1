import React, { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { inventoryAPI, signalsAPI } from '../services/api';
import { ApiError } from '../services/apiErrors';
import type { AISystem, OperationalSignal, SignalSeverity, SignalStatus, SignalType } from '../types';

const SignalsPage: React.FC = () => {
    const { token, expireSession } = useAuth();
    const [systems, setSystems] = useState<AISystem[]>([]);
    const [signals, setSignals] = useState<OperationalSignal[]>([]);
    const [systemFilter, setSystemFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState<SignalStatus | ''>('');
    const [showForm, setShowForm] = useState(false);
    const [error, setError] = useState('');
    const [form, setForm] = useState({
        ai_system_id: '', signal_type: 'incident' as SignalType, severity: 'medium' as SignalSeverity,
        title: '', description: '', reported_by: '', reported_on: new Date().toISOString().slice(0, 10),
        owner: '', response_action: '', reviewer_notes: '',
    });

    const loadSignals = useCallback(async () => {
        if (!token) return;
        try {
            setError('');
            setSignals(await signalsAPI.list(token, { aiSystemId: systemFilter ? Number(systemFilter) : undefined, status: statusFilter || undefined }));
        } catch (err) {
            if (err instanceof ApiError && err.kind === 'unauthorized') { expireSession(); return; }
            setError(err instanceof ApiError ? err.message : 'We could not load operational signals.');
        }
    }, [token, systemFilter, statusFilter, expireSession]);

    useEffect(() => {
        if (!token) return;
        inventoryAPI.list(token).then(setSystems).catch(() => setError('We could not load your AI-system inventory.'));
    }, [token]);
    useEffect(() => {
        const timer = window.setTimeout(() => { void loadSignals(); }, 0);
        return () => window.clearTimeout(timer);
    }, [loadSignals]);

    const submit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!token) return;
        try {
            await signalsAPI.create(token, { ...form, ai_system_id: Number(form.ai_system_id), status: 'new', finding_id: undefined, review_id: undefined });
            setShowForm(false);
            setForm({ ...form, title: '', description: '', response_action: '', reviewer_notes: '' });
            await loadSignals();
        } catch (err) {
            if (err instanceof ApiError && err.kind === 'unauthorized') { expireSession(); return; }
            setError(err instanceof ApiError ? err.message : 'We could not save this signal.');
        }
    };

    const closeSignal = async (signal: OperationalSignal) => {
        if (!token) return;
        try { await signalsAPI.update(token, signal.id, { status: 'closed' }); await loadSignals(); }
        catch (err) { setError(err instanceof ApiError ? err.message : 'We could not update this signal.'); }
    };

    return <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm"><div className="max-w-7xl mx-auto px-4 py-4"><h1 className="text-2xl font-bold text-gray-800">Operational signals</h1><p className="text-sm text-gray-600">Record incidents, feedback, and material changes so they can inform human review.</p></div></nav>
        <main className="max-w-7xl mx-auto px-4 py-8">
            <section className="card mb-6 border-l-4 border-orange-500"><p className="text-sm text-gray-700">These are working governance records entered by your team. They are not legal incident classifications or objective safety determinations.</p></section>
            <div className="card mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div className="flex flex-col gap-3 sm:flex-row"><label className="text-sm text-gray-700">AI system<select className="input-field mt-1" value={systemFilter} onChange={e => setSystemFilter(e.target.value)}><option value="">All systems</option>{systems.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label><label className="text-sm text-gray-700">Status<select className="input-field mt-1" value={statusFilter} onChange={e => setStatusFilter(e.target.value as SignalStatus | '')}><option value="">All statuses</option><option value="new">New</option><option value="triaged">Triaged</option><option value="investigating">Investigating</option><option value="closed">Closed</option></select></label></div>
                <button className="btn-primary" onClick={() => setShowForm(true)}>+ Add signal</button>
            </div>
            {error && <div role="alert" className="card mb-6 border border-red-200 bg-red-50 text-red-700">{error}</div>}
            {showForm && <form className="card mb-6 space-y-4" onSubmit={submit}><h2 className="text-xl font-bold text-gray-800">Add an operational signal</h2><div className="grid gap-4 sm:grid-cols-2"><label className="text-sm">AI system<select className="input-field mt-1" required value={form.ai_system_id} onChange={e => setForm({ ...form, ai_system_id: e.target.value })}><option value="">Choose a system</option>{systems.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label><label className="text-sm">Type<select className="input-field mt-1" value={form.signal_type} onChange={e => setForm({ ...form, signal_type: e.target.value as SignalType })}><option value="incident">Incident</option><option value="feedback">User feedback</option><option value="material_change">Material change</option></select></label><label className="text-sm">Severity<select className="input-field mt-1" value={form.severity} onChange={e => setForm({ ...form, severity: e.target.value as SignalSeverity })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></label><label className="text-sm">Discovered date<input className="input-field mt-1" type="date" required value={form.reported_on} onChange={e => setForm({ ...form, reported_on: e.target.value })} /></label></div><label className="text-sm">Title<input className="input-field mt-1" required maxLength={255} value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} /></label><label className="text-sm">What happened or what was reported?<textarea className="input-field mt-1" required rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} /></label><div className="grid gap-4 sm:grid-cols-2"><label className="text-sm">Reported by<input className="input-field mt-1" required value={form.reported_by} onChange={e => setForm({ ...form, reported_by: e.target.value })} /></label><label className="text-sm">Owner<input className="input-field mt-1" value={form.owner} onChange={e => setForm({ ...form, owner: e.target.value })} /></label></div><label className="text-sm">Response or next action<textarea className="input-field mt-1" rows={2} value={form.response_action} onChange={e => setForm({ ...form, response_action: e.target.value })} /></label><label className="text-sm">Reviewer notes<textarea className="input-field mt-1" rows={2} value={form.reviewer_notes} onChange={e => setForm({ ...form, reviewer_notes: e.target.value })} /></label><div className="flex gap-2"><button className="btn-primary" type="submit">Save signal</button><button className="btn-secondary" type="button" onClick={() => setShowForm(false)}>Cancel</button></div></form>}
            <div className="space-y-4">{signals.length === 0 ? <div className="card text-center text-gray-600">No signals match these filters. Record the first signal when your team receives feedback or identifies a change.</div> : signals.map(signal => <article className="card" key={signal.id}><div className="flex flex-wrap items-start justify-between gap-3"><div><div className="flex flex-wrap gap-2 text-xs font-semibold uppercase"><span className="rounded bg-gray-100 px-2 py-1">{signal.signal_type.replace('_', ' ')}</span><span className="rounded bg-orange-100 px-2 py-1 text-orange-800">{signal.severity}</span><span className="rounded bg-blue-100 px-2 py-1 text-blue-800">{signal.status}</span></div><h2 className="mt-2 text-xl font-bold text-gray-800">{signal.title}</h2></div>{signal.status !== 'closed' && <button className="btn-secondary" onClick={() => closeSignal(signal)}>Mark closed</button>}</div><p className="mt-3 text-gray-700">{signal.description}</p><p className="mt-3 text-sm text-gray-500">Reported {signal.reported_on} by {signal.reported_by}{signal.owner ? ` · Owner: ${signal.owner}` : ''}</p>{signal.response_action && <p className="mt-3 text-sm"><strong>Response:</strong> {signal.response_action}</p>}</article>)}</div>
        </main>
    </div>;
};
export default SignalsPage;
