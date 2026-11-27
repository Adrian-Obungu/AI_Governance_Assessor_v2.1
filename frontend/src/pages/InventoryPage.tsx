import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../services/apiErrors';
import { inventoryAPI } from '../services/api';
import type { AISystem, AISystemLifecycle } from '../types';

const lifecycleLabels: Record<AISystemLifecycle, string> = {
    discovery: 'Exploring',
    pilot: 'Pilot',
    in_production: 'In production',
    retired: 'Retired',
};

const initialForm = {
    name: '', purpose: '', department: '', business_owner: '', provider: '',
    lifecycle_stage: 'discovery' as AISystemLifecycle,
    geographies: '', data_categories: '', affected_groups: '', review_date: '',
};

type FormState = typeof initialForm;

const splitList = (value: string) => value.split(',').map((item) => item.trim()).filter(Boolean);

const InventoryPage: React.FC = () => {
    const { token, email, logout, expireSession } = useAuth();
    const navigate = useNavigate();
    const [systems, setSystems] = useState<AISystem[]>([]);
    const [form, setForm] = useState<FormState>(initialForm);
    const [showForm, setShowForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const loadSystems = useCallback(async () => {
        if (!token) return;
        try {
            setLoading(true);
            setError('');
            setSystems(await inventoryAPI.list(token));
        } catch (requestError) {
            if (requestError instanceof ApiError && requestError.kind === 'unauthorized') {
                expireSession();
                return;
            }
            setError(requestError instanceof ApiError ? requestError.message : 'We could not load your inventory.');
        } finally {
            setLoading(false);
        }
    }, [token, expireSession]);

    useEffect(() => { loadSystems(); }, [loadSystems]);

    const updateField = (field: keyof FormState, value: string) => {
        setForm((current) => ({ ...current, [field]: value }));
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!token) return;
        try {
            setSaving(true);
            setError('');
            await inventoryAPI.create(token, {
                name: form.name.trim(), purpose: form.purpose.trim(),
                department: form.department.trim() || undefined,
                business_owner: form.business_owner.trim() || undefined,
                provider: form.provider.trim() || undefined,
                lifecycle_stage: form.lifecycle_stage,
                geographies: splitList(form.geographies),
                data_categories: splitList(form.data_categories),
                affected_groups: splitList(form.affected_groups),
                review_date: form.review_date || undefined,
            });
            setForm(initialForm);
            setShowForm(false);
            await loadSystems();
        } catch (requestError) {
            if (requestError instanceof ApiError && requestError.kind === 'unauthorized') {
                expireSession();
                return;
            }
            setError(requestError instanceof ApiError ? requestError.message : 'We could not save this system. Your entries are still here.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-sm">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <button type="button" onClick={() => navigate('/dashboard')} className="text-xl font-bold text-gray-800">AI Governance Assessor</button>
                    <div className="flex items-center gap-4"><span className="hidden sm:inline text-gray-600">{email}</span><button onClick={logout} className="btn-secondary">Logout</button></div>
                </div>
            </nav>
            <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
                    <div><p className="text-sm font-semibold uppercase tracking-wide text-primary-600">Step 1 · Context</p><h1 className="mt-1 text-3xl font-bold text-gray-800">Your AI-system inventory</h1><p className="mt-2 max-w-2xl text-gray-600">Start with the system you need to understand. This context helps you choose the right governance work next; it is not a legal classification.</p></div>
                    <button type="button" onClick={() => { setError(''); setShowForm(true); }} className="btn-primary whitespace-nowrap">+ Add AI system</button>
                </div>
                {error && <div role="alert" className="card mb-6 border border-red-200 bg-red-50 text-red-700">{error}<button type="button" className="ml-3 underline" onClick={loadSystems}>Retry</button></div>}
                {loading ? <div className="card text-gray-600">Loading your systems...</div> : systems.length === 0 ? (
                    <div className="card max-w-2xl"><h2 className="text-2xl font-bold text-gray-800">No systems added yet</h2><p className="mt-2 text-gray-600">Capture one real AI tool, model, or AI-enabled process before starting a questionnaire. You can add more later.</p><button type="button" onClick={() => setShowForm(true)} className="btn-primary mt-5">Add your first system</button></div>
                ) : <div className="grid gap-5 md:grid-cols-2">{systems.map((system) => <article key={system.id} className="card"><div className="flex justify-between gap-3"><div><h2 className="text-xl font-semibold text-gray-800">{system.name}</h2><p className="mt-1 text-gray-600 line-clamp-3">{system.purpose}</p></div><span className="h-fit rounded-full bg-primary-100 px-3 py-1 text-xs font-semibold text-primary-700">{lifecycleLabels[system.lifecycle_stage]}</span></div><dl className="mt-5 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-gray-500">Owner</dt><dd className="font-medium text-gray-800">{system.business_owner || 'Not set'}</dd></div><div><dt className="text-gray-500">Provider</dt><dd className="font-medium text-gray-800">{system.provider || 'Not set'}</dd></div><div><dt className="text-gray-500">Review date</dt><dd className="font-medium text-gray-800">{system.review_date || 'Not set'}</dd></div><div><dt className="text-gray-500">Department</dt><dd className="font-medium text-gray-800">{system.department || 'Not set'}</dd></div></dl></article>)}</div>}
            </main>
            {showForm && <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 p-4"><div className="card mx-auto my-6 max-w-2xl" role="dialog" aria-modal="true" aria-labelledby="inventory-form-title"><div className="flex justify-between gap-4"><div><h2 id="inventory-form-title" className="text-2xl font-bold text-gray-800">Add an AI system</h2><p className="mt-1 text-sm text-gray-600">Short answers are enough. You can improve this context later.</p></div><button type="button" onClick={() => setShowForm(false)} className="text-2xl text-gray-500" aria-label="Close form">×</button></div><form onSubmit={handleSubmit} className="mt-6 space-y-5"><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-name">What is it called?</label><input id="system-name" className="input-field mt-1" value={form.name} onChange={(e) => updateField('name', e.target.value)} required placeholder="e.g. Customer support assistant" /></div><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-purpose">What does it do?</label><textarea id="system-purpose" className="input-field mt-1" rows={3} value={form.purpose} onChange={(e) => updateField('purpose', e.target.value)} required placeholder="Describe the decision, task, or service it supports." /><p className="mt-1 text-xs text-gray-500">Plain language is best. Avoid entering confidential personal data.</p></div><div className="grid gap-4 sm:grid-cols-2"><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-department">Department</label><input id="system-department" className="input-field mt-1" value={form.department} onChange={(e) => updateField('department', e.target.value)} placeholder="e.g. Customer Operations" /></div><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-owner">Business owner</label><input id="system-owner" className="input-field mt-1" value={form.business_owner} onChange={(e) => updateField('business_owner', e.target.value)} placeholder="Person or team accountable" /></div></div><div className="grid gap-4 sm:grid-cols-2"><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-provider">Provider or vendor</label><input id="system-provider" className="input-field mt-1" value={form.provider} onChange={(e) => updateField('provider', e.target.value)} placeholder="Internal, vendor, or provider" /></div><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-stage">Where is it now?</label><select id="system-stage" className="input-field mt-1" value={form.lifecycle_stage} onChange={(e) => updateField('lifecycle_stage', e.target.value)}>{Object.entries(lifecycleLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div></div><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-geographies">Where is it used?</label><input id="system-geographies" className="input-field mt-1" value={form.geographies} onChange={(e) => updateField('geographies', e.target.value)} placeholder="Comma-separated, e.g. Kenya, Uganda" /></div><div className="grid gap-4 sm:grid-cols-2"><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-data">What data does it use?</label><input id="system-data" className="input-field mt-1" value={form.data_categories} onChange={(e) => updateField('data_categories', e.target.value)} placeholder="e.g. customer messages, IDs" /></div><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-groups">Who may be affected?</label><input id="system-groups" className="input-field mt-1" value={form.affected_groups} onChange={(e) => updateField('affected_groups', e.target.value)} placeholder="e.g. customers, staff" /></div></div><div><label className="block text-sm font-medium text-gray-700" htmlFor="system-review">When should it be reviewed next?</label><input id="system-review" type="date" className="input-field mt-1" value={form.review_date} onChange={(e) => updateField('review_date', e.target.value)} /><p className="mt-1 text-xs text-gray-500">Choose a date that fits your team’s review rhythm.</p></div>{error && <div role="alert" className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}<div className="flex flex-col-reverse gap-3 sm:flex-row"><button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button><button type="submit" className="btn-primary flex-1" disabled={saving}>{saving ? 'Saving...' : 'Save AI system'}</button></div></form></div></div>}
        </div>
    );
};

export default InventoryPage;
