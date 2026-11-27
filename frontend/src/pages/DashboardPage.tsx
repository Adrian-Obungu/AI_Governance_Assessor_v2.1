import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI, inventoryAPI } from '../services/api';
import { ApiError } from '../services/apiErrors';
import type { AISystem, Assessment } from '../types';

const assessmentTemplates = [
    {
        name: 'AI governance baseline',
        title: 'AI System Governance Baseline',
        description: 'A first review of privacy, model risk, ethics, and regulatory readiness for an AI system.',
    },
    {
        name: 'Generative AI use-case review',
        title: 'Generative AI Use-Case Review',
        description: 'A structured review of governance readiness for a generative AI use case or deployment.',
    },
    {
        name: 'AI vendor review',
        title: 'AI Vendor and Third-Party Review',
        description: 'A governance baseline for an AI product, model, or service supplied by a third party.',
    },
    {
        name: 'Custom assessment',
        title: '',
        description: '',
    },
];

const DashboardPage: React.FC = () => {
    const [assessments, setAssessments] = useState<Assessment[]>([]);
    const [systems, setSystems] = useState<AISystem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newTitle, setNewTitle] = useState(assessmentTemplates[0].title);
    const [newDescription, setNewDescription] = useState(assessmentTemplates[0].description);
    const [selectedTemplate, setSelectedTemplate] = useState('AI governance baseline');
    const [selectedSystemId, setSelectedSystemId] = useState('');
    const [error, setError] = useState('');
    const createButtonRef = useRef<HTMLButtonElement>(null);
    const closeModalRef = useRef<HTMLButtonElement>(null);
    const modalWasOpen = useRef(false);
    const { token, email, logout, expireSession } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (showCreateModal) {
            modalWasOpen.current = true;
            closeModalRef.current?.focus();
        } else if (modalWasOpen.current) {
            createButtonRef.current?.focus();
        }
    }, [showCreateModal]);

    const loadAssessments = useCallback(async () => {
        if (!token) return;
        try {
            setLoading(true);
            setError('');
            const data = await assessmentAPI.listAssessments(token);
            setAssessments(data);
        } catch (error) {
            console.error('Failed to load assessments:', error);
            if (error instanceof ApiError && error.kind === 'unauthorized') {
                expireSession();
                return;
            }
            setError(error instanceof ApiError ? error.message : 'We could not load assessments. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [token, expireSession]);

    useEffect(() => {
        loadAssessments();
    }, [loadAssessments]);

    const loadInventory = useCallback(async () => {
        if (!token) return;
        try {
            setSystems(await inventoryAPI.list(token));
        } catch (error) {
            if (error instanceof ApiError && error.kind === 'unauthorized') {
                expireSession();
                return;
            }
            setError('We could not load your AI-system context. You can continue without linking one.');
        }
    }, [token, expireSession]);

    useEffect(() => {
        loadInventory();
    }, [loadInventory]);

    const handleCreateAssessment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;

        try {
            setError('');
            await assessmentAPI.createAssessment(token, newTitle, newDescription, selectedSystemId ? Number(selectedSystemId) : undefined);
            setShowCreateModal(false);
            setNewTitle(assessmentTemplates[0].title);
            setNewDescription(assessmentTemplates[0].description);
            setSelectedTemplate('AI governance baseline');
            setSelectedSystemId('');
            loadAssessments();
        } catch (error) {
            console.error('Failed to create assessment:', error);
            setError('We could not create the assessment. Please try again.');
        }
    };

    const handleTemplateChange = (templateName: string) => {
        setSelectedTemplate(templateName);
        const template = assessmentTemplates.find((item) => item.name === templateName);
        if (!template || templateName === 'Custom assessment') {
            setNewTitle('');
            setNewDescription('');
            return;
        }
        setNewTitle(template.title);
        setNewDescription(template.description);
    };

    const getStatusBadge = (status: string) => {
        const colors = {
            draft: 'bg-gray-200 text-gray-800',
            in_progress: 'bg-blue-200 text-blue-800',
            completed: 'bg-green-200 text-green-800',
        };
        return colors[status as keyof typeof colors] || colors.draft;
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">AI Governance Assessor</h1>
                    <div className="flex items-center gap-4">
                        <span className="text-gray-600">{email}</span>
                        <button onClick={logout} className="btn-secondary">
                            Logout
                        </button>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <section className="card mb-8 bg-gradient-to-r from-primary-700 to-primary-500 text-white">
                    <p className="text-sm font-semibold uppercase tracking-wide text-primary-100">AI governance readiness workspace</p>
                    <h2 className="mt-2 text-3xl font-bold">Turn governance questions into an improvement plan.</h2>
                    <p className="mt-3 max-w-3xl text-primary-50">
                        Review an AI system across data privacy, model risk, ethics, and regulatory compliance. This tool provides a structured readiness assessment and recommendations; it is not a legal certification or compliance decision.
                    </p>
                    <div className="mt-5 grid gap-3 sm:grid-cols-4" aria-label="Assessment domains">
                        {['Data privacy', 'Model risk', 'AI ethics', 'Compliance'].map((domain) => (
                            <div key={domain} className="rounded bg-white/15 px-3 py-2 text-sm">{domain}</div>
                        ))}
                    </div>
                </section>
                <section className="card mb-8 flex flex-col gap-4 border-l-4 border-primary-500 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <p className="text-sm font-semibold uppercase tracking-wide text-primary-600">Start with context</p>
                        <h2 className="mt-1 text-xl font-bold text-gray-800">Record the AI system before scoring it.</h2>
                        <p className="mt-1 max-w-2xl text-gray-600">Capture its purpose, owner, provider, and operating context so the assessment has something real to refer to.</p>
                    </div>
                    <button type="button" onClick={() => navigate('/inventory')} className="btn-secondary whitespace-nowrap">Open AI-system inventory</button>
                </section>
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-3xl font-bold text-gray-800">My Assessments</h2>
                        <p className="mt-1 text-gray-600">Track governance reviews and return to unfinished work.</p>
                    </div>
                    <button ref={createButtonRef} onClick={() => { setError(''); setShowCreateModal(true); }} className="btn-primary">
                        + New Assessment
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <div className="text-gray-600">Loading assessments...</div>
                    </div>
                ) : error ? (
                    <div className="card text-center py-12" role="alert">
                        <p className="text-red-700">{error}</p>
                        <button onClick={loadAssessments} className="btn-secondary mt-4">Retry</button>
                    </div>
                ) : assessments.length === 0 ? (
                    <div className="card text-center py-12">
                        <div className="mx-auto max-w-2xl">
                            <h3 className="text-2xl font-bold text-gray-800">Start with a governance baseline</h3>
                            <p className="mt-3 text-gray-600">Choose a suggested assessment focus, answer the four governance sections, and receive a scored readiness summary with recommendations.</p>
                        </div>
                        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
                            Start first assessment
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {assessments.map((assessment) => (
                            <button
                                type="button"
                                key={assessment.id}
                                className="card w-full text-left hover:shadow-lg transition-shadow focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                                onClick={() => navigate(`/assessment/${assessment.id}`)}
                                aria-label={`Open assessment ${assessment.title}`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-xl font-semibold text-gray-800">{assessment.title}</h3>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(assessment.status)}`}>
                                        {assessment.status.replace('_', ' ')}
                                    </span>
                                </div>
                                {assessment.description && (
                                    <p className="text-gray-600 text-sm mb-4">{assessment.description}</p>
                                )}
                                <div className="text-sm text-gray-500">
                                    Created: {new Date(assessment.created_at).toLocaleDateString()}
                                </div>
                                {assessment.results.length > 0 && (
                                    <div className="mt-2 text-sm text-primary-600">
                                        {assessment.results.length} / 4 categories completed
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                )}
            </main>

            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="card max-w-lg w-full" role="dialog" aria-modal="true" aria-labelledby="create-assessment-title">
                        <div className="flex items-start justify-between gap-4">
                            <h3 id="create-assessment-title" className="text-2xl font-bold text-gray-800 mb-2">Start a governance assessment</h3>
                            <button
                                ref={closeModalRef}
                                type="button"
                                onClick={() => setShowCreateModal(false)}
                                className="text-gray-500 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
                                aria-label="Close assessment dialog"
                            >
                                ×
                            </button>
                        </div>
                        <p className="text-sm text-gray-600 mb-4">The suggested names help frame your review. They do not change the current four-domain questionnaire.</p>
                        <form onSubmit={handleCreateAssessment} className="space-y-4">
                            <div>
                                <label htmlFor="assessment-template" className="block text-sm font-medium text-gray-700 mb-1">
                                    Assessment focus
                                </label>
                                <select
                                    id="assessment-template"
                                    value={selectedTemplate}
                                    onChange={(e) => handleTemplateChange(e.target.value)}
                                    className="input-field"
                                >
                                    {assessmentTemplates.map((template) => <option key={template.name} value={template.name}>{template.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label htmlFor="assessment-system" className="block text-sm font-medium text-gray-700 mb-1">
                                    AI system context (optional)
                                </label>
                                <select
                                    id="assessment-system"
                                    value={selectedSystemId}
                                    onChange={(e) => setSelectedSystemId(e.target.value)}
                                    className="input-field"
                                >
                                    <option value="">Continue without linking a system</option>
                                    {systems.map((system) => (
                                        <option key={system.id} value={system.id}>{system.name}</option>
                                    ))}
                                </select>
                                <p className="mt-1 text-xs text-gray-500">Linking adds context; it does not change the questions or score.</p>
                            </div>
                            <div>
                                <label htmlFor="assessment-title" className="block text-sm font-medium text-gray-700 mb-1">
                                    Title
                                </label>
                                <input
                                    id="assessment-title"
                                    type="text"
                                    value={newTitle}
                                    onChange={(e) => setNewTitle(e.target.value)}
                                    className="input-field"
                                    placeholder="Q4 2024 AI System Assessment"
                                    required
                                />
                            </div>
                            <div>
                                <label htmlFor="assessment-description" className="block text-sm font-medium text-gray-700 mb-1">
                                    Description (optional)
                                </label>
                                <textarea
                                    id="assessment-description"
                                    value={newDescription}
                                    onChange={(e) => setNewDescription(e.target.value)}
                                    className="input-field"
                                    rows={3}
                                    placeholder="Assessment for our customer service AI system"
                                />
                            </div>
                            {error && <div role="alert" className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}
                            <div className="flex gap-2">
                                <button type="submit" className="btn-primary flex-1">
                                    Create
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="btn-secondary flex-1"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DashboardPage;
