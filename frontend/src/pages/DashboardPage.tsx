import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI } from '../services/api';
import type { Assessment } from '../types';

const DashboardPage: React.FC = () => {
    const [assessments, setAssessments] = useState<Assessment[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newTitle, setNewTitle] = useState('');
    const [newDescription, setNewDescription] = useState('');
    const { token, email, logout } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        loadAssessments();
    }, []);

    const loadAssessments = async () => {
        if (!token) return;
        try {
            const data = await assessmentAPI.listAssessments(token);
            setAssessments(data);
        } catch (error) {
            console.error('Failed to load assessments:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateAssessment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;

        try {
            await assessmentAPI.createAssessment(token, newTitle, newDescription);
            setShowCreateModal(false);
            setNewTitle('');
            setNewDescription('');
            loadAssessments();
        } catch (error) {
            console.error('Failed to create assessment:', error);
        }
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
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-3xl font-bold text-gray-800">My Assessments</h2>
                    <button onClick={() => setShowCreateModal(true)} className="btn-primary">
                        + New Assessment
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <div className="text-gray-600">Loading assessments...</div>
                    </div>
                ) : assessments.length === 0 ? (
                    <div className="card text-center py-12">
                        <p className="text-gray-600 mb-4">No assessments yet. Create your first one!</p>
                        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
                            Create Assessment
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {assessments.map((assessment) => (
                            <div
                                key={assessment.id}
                                className="card hover:shadow-lg transition-shadow cursor-pointer"
                                onClick={() => navigate(`/assessment/${assessment.id}`)}
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
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="card max-w-md w-full">
                        <h3 className="text-2xl font-bold text-gray-800 mb-4">Create New Assessment</h3>
                        <form onSubmit={handleCreateAssessment} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Title
                                </label>
                                <input
                                    type="text"
                                    value={newTitle}
                                    onChange={(e) => setNewTitle(e.target.value)}
                                    className="input-field"
                                    placeholder="Q4 2024 AI System Assessment"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Description (optional)
                                </label>
                                <textarea
                                    value={newDescription}
                                    onChange={(e) => setNewDescription(e.target.value)}
                                    className="input-field"
                                    rows={3}
                                    placeholder="Assessment for our customer service AI system"
                                />
                            </div>
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
