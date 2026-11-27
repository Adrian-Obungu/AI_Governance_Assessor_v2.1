import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../services/apiErrors';
import { assessmentAPI, evidenceAPI, inventoryAPI } from '../services/api';
import type { AISystem, Assessment, EvidenceRecord, EvidenceStatus, EvidenceType } from '../types';

const evidenceTypeLabels: Record<EvidenceType, string> = {
    policy: 'Policy', procedure: 'Procedure', contract: 'Contract', technical_document: 'Technical document',
    training_record: 'Training record', audit_record: 'Audit record', review_note: 'Review note', other: 'Other',
};
const statusLabels: Record<EvidenceStatus, string> = { draft: 'Draft', submitted: 'Submitted', reviewed: 'Reviewed', needs_update: 'Needs update' };
const statusStyles: Record<EvidenceStatus, string> = {
    draft: 'bg-gray-100 text-gray-700', submitted: 'bg-blue-100 text-blue-700', reviewed: 'bg-green-100 text-green-700', needs_update: 'bg-amber-100 text-amber-800',
};
const initialForm = { ai_system_id: '', assessment_id: '', title: '', description: '', evidence_type: 'policy' as EvidenceType, source_location: '', owner: '', collected_on: '', review_date: '', status: 'draft' as EvidenceStatus, reviewer_notes: '' };
type FormState = typeof initialForm;

const EvidencePage: React.FC = () => {
    const { token, email, logout, expireSession } = useAuth();
    const navigate = useNavigate();
    const [systems, setSystems] = useState<AISystem[]>([]);
    const [assessments, setAssessments] = useState<Assessment[]>([]);
    const [records, setRecords] = useState<EvidenceRecord[]>([]);
    const [form, setForm] = useState<FormState>(initialForm);
    const [systemFilter, setSystemFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const handleError = useCallback((requestError: unknown, fallback: string) => {
        if (requestError instanceof ApiError && requestError.kind === 'unauthorized') { expireSession(); return true; }
        setError(requestError instanceof ApiError ? requestError.message : fallback);
        return false;
    }, [expireSession]);
    const loadRecords = useCallback(async () => {
        if (!token) return;
        try { setLoading(true); setError(''); setRecords(await evidenceAPI.list(token, { aiSystemId: systemFilter ? Number(systemFilter) : undefined, status: (statusFilter || undefined) as EvidenceStatus | undefined })); }
        catch (requestError) { handleError(requestError, 'We could not load your evidence records.'); }
        finally { setLoading(false); }
    }, [token, systemFilter, statusFilter, handleError]);
    useEffect(() => { loadRecords(); }, [loadRecords]);
    useEffect(() => {
        if (!token) return;
        Promise.all([inventoryAPI.list(token), assessmentAPI.listAssessments(token)]).then(([systemData, assessmentData]) => { setSystems(systemData); setAssessments(assessmentData); }).catch((requestError) => { handleError(requestError, 'We could not load context for the evidence form.'); });
    }, [token, handleError]);

    const updateField = (field: keyof FormState, value: string) => setForm((current) => ({ ...current, [field]: value }));
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!token) return;
        try {
            setSaving(true); setError('');
            await evidenceAPI.create(token, { ai_system_id: Number(form.ai_system_id), assessment_id: form.assessment_id ? Number(form.assessment_id) : undefined, title: form.title.trim(), description: form.description.trim(), evidence_type: form.evidence_type, source_location: form.source_location.trim() || undefined, owner: form.owner.trim() || undefined, collected_on: form.collected_on || undefined, review_date: form.review_date || undefined, status: form.status, reviewer_notes: form.reviewer_notes.trim() || undefined });
            setForm(initialForm); setShowForm(false); await loadRecords();
        } catch (requestError) { handleError(requestError, 'We could not save this record. Your entries are still here.'); }
        finally { setSaving(false); }
    };

    return <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm"><div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center"><button type="button" onClick={() => navigate('/dashboard')} className="text-xl font-bold text-gray-800">AI Governance Assessor</button><div className="flex items-center gap-4"><span className="hidden sm:inline text-gray-600">{email}</span><button onClick={logout} className="btn-secondary">Logout</button></div></div></nav>
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8"><div><p className="text-sm font-semibold uppercase tracking-wide text-primary-600">Step 3 · Evidence</p><h1 className="mt-1 text-3xl font-bold text-gray-800">Evidence register</h1><p className="mt-2 max-w-2xl text-gray-600">Record what exists, where it can be found, and when it should be reviewed. This first version stores metadata only—no files are uploaded.</p></div><button type="button" onClick={() => { setError(''); setShowForm(true); }} className="btn-primary whitespace-nowrap">+ Add evidence record</button></div>
            <div className="card mb-6"><div className="flex flex-col gap-3 sm:flex-row sm:items-end"><div className="flex-1"><label htmlFor="evidence-system-filter" className="block text-sm font-medium text-gray-700">Filter by AI system</label><select id="evidence-system-filter" className="input-field mt-1" value={systemFilter} onChange={(event) => setSystemFilter(event.target.value)}><option value="">All systems</option>{systems.map((system) => <option key={system.id} value={system.id}>{system.name}</option>)}</select></div><div className="flex-1"><label htmlFor="evidence-status-filter" className="block text-sm font-medium text-gray-700">Filter by status</label><select id="evidence-status-filter" className="input-field mt-1" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="">All statuses</option>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div></div></div>
            {error && <div role="alert" className="card mb-6 border border-red-200 bg-red-50 text-red-700">{error}<button type="button" onClick={loadRecords} className="ml-3 underline">Retry</button></div>}
            {loading ? <div className="card text-gray-600">Loading evidence records...</div> : records.length === 0 ? <div className="card max-w-2xl"><h2 className="text-2xl font-bold text-gray-800">No evidence records yet</h2><p className="mt-2 text-gray-600">Start with a policy, procedure, contract, technical document, or review note connected to an AI system.</p><button type="button" onClick={() => setShowForm(true)} className="btn-primary mt-5">Add the first record</button></div> : <div className="grid gap-5 md:grid-cols-2">{records.map((record) => { const system = systems.find((item) => item.id === record.ai_system_id); return <article key={record.id} className="card"><div className="flex justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-wide text-gray-500">{evidenceTypeLabels[record.evidence_type]}</p><h2 className="mt-1 text-xl font-semibold text-gray-800">{record.title}</h2></div><span className={`h-fit rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[record.status]}`}>{statusLabels[record.status]}</span></div><p className="mt-3 text-gray-600">{record.description}</p><dl className="mt-5 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-gray-500">AI system</dt><dd className="font-medium text-gray-800">{system?.name || `System #${record.ai_system_id}`}</dd></div><div><dt className="text-gray-500">Owner</dt><dd className="font-medium text-gray-800">{record.owner || 'Not set'}</dd></div><div><dt className="text-gray-500">Collected</dt><dd className="font-medium text-gray-800">{record.collected_on || 'Not set'}</dd></div><div><dt className="text-gray-500">Review date</dt><dd className="font-medium text-gray-800">{record.review_date || 'Not set'}</dd></div></dl>{record.source_location && <p className="mt-4 text-sm text-gray-500">Location: <span className="text-gray-700">{record.source_location}</span></p>}</article>; })}</div>}
        </main>
        {showForm && <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 p-4"><div className="card mx-auto my-6 max-w-2xl" role="dialog" aria-modal="true" aria-labelledby="evidence-form-title"><div className="flex justify-between gap-4"><div><h2 id="evidence-form-title" className="text-2xl font-bold text-gray-800">Add an evidence record</h2><p className="mt-1 text-sm text-gray-600">Describe the evidence and its location; do not upload confidential files here.</p></div><button type="button" onClick={() => setShowForm(false)} className="text-2xl text-gray-500" aria-label="Close form">×</button></div><form onSubmit={handleSubmit} className="mt-6 space-y-5"><div className="grid gap-4 sm:grid-cols-2"><div><label htmlFor="evidence-system" className="block text-sm font-medium text-gray-700">AI system</label><select id="evidence-system" className="input-field mt-1" value={form.ai_system_id} onChange={(event) => updateField('ai_system_id', event.target.value)} required><option value="">Select a system</option>{systems.map((system) => <option key={system.id} value={system.id}>{system.name}</option>)}</select></div><div><label htmlFor="evidence-assessment" className="block text-sm font-medium text-gray-700">Assessment (optional)</label><select id="evidence-assessment" className="input-field mt-1" value={form.assessment_id} onChange={(event) => updateField('assessment_id', event.target.value)}><option value="">No linked assessment</option>{assessments.map((assessment) => <option key={assessment.id} value={assessment.id}>{assessment.title}</option>)}</select></div></div><div><label htmlFor="evidence-title" className="block text-sm font-medium text-gray-700">Evidence title</label><input id="evidence-title" className="input-field mt-1" value={form.title} onChange={(event) => updateField('title', event.target.value)} required placeholder="e.g. Customer data handling policy" /></div><div><label htmlFor="evidence-description" className="block text-sm font-medium text-gray-700">What does it show?</label><textarea id="evidence-description" className="input-field mt-1" rows={3} value={form.description} onChange={(event) => updateField('description', event.target.value)} required placeholder="Summarise the relevant control, process, or decision in plain language." /></div><div className="grid gap-4 sm:grid-cols-2"><div><label htmlFor="evidence-type" className="block text-sm font-medium text-gray-700">Evidence type</label><select id="evidence-type" className="input-field mt-1" value={form.evidence_type} onChange={(event) => updateField('evidence_type', event.target.value)}>{Object.entries(evidenceTypeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div><div><label htmlFor="evidence-status" className="block text-sm font-medium text-gray-700">Status</label><select id="evidence-status" className="input-field mt-1" value={form.status} onChange={(event) => updateField('status', event.target.value)}>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div></div><div className="grid gap-4 sm:grid-cols-2"><div><label htmlFor="evidence-owner" className="block text-sm font-medium text-gray-700">Evidence owner</label><input id="evidence-owner" className="input-field mt-1" value={form.owner} onChange={(event) => updateField('owner', event.target.value)} placeholder="Person or team" /></div><div><label htmlFor="evidence-location" className="block text-sm font-medium text-gray-700">Source location</label><input id="evidence-location" className="input-field mt-1" value={form.source_location} onChange={(event) => updateField('source_location', event.target.value)} placeholder="Internal reference or link" /></div></div><div className="grid gap-4 sm:grid-cols-2"><div><label htmlFor="evidence-collected" className="block text-sm font-medium text-gray-700">Collected on</label><input id="evidence-collected" type="date" className="input-field mt-1" value={form.collected_on} onChange={(event) => updateField('collected_on', event.target.value)} /></div><div><label htmlFor="evidence-review" className="block text-sm font-medium text-gray-700">Review date</label><input id="evidence-review" type="date" className="input-field mt-1" value={form.review_date} onChange={(event) => updateField('review_date', event.target.value)} /></div></div><div><label htmlFor="evidence-notes" className="block text-sm font-medium text-gray-700">Reviewer notes (optional)</label><textarea id="evidence-notes" className="input-field mt-1" rows={2} value={form.reviewer_notes} onChange={(event) => updateField('reviewer_notes', event.target.value)} /></div>{error && <div role="alert" className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}<div className="flex flex-col-reverse gap-3 sm:flex-row"><button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button><button type="submit" className="btn-primary flex-1" disabled={saving || systems.length === 0}>{saving ? 'Saving...' : 'Save evidence record'}</button></div></form></div></div>}
    </div>;
};

export default EvidencePage;
