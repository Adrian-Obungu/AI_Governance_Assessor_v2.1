import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI } from '../services/api';
import type { AssessmentSummary } from '../types';

const ReportPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [summary, setSummary] = useState<AssessmentSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);
    const { token } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        loadSummary();
    }, [id]);

    const loadSummary = async () => {
        if (!token || !id) return;
        try {
            const data = await assessmentAPI.getSummary(token, parseInt(id));
            setSummary(data);
        } catch (error) {
            console.error('Failed to load summary:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async (format: 'csv' | 'pdf') => {
        if (!token || !id) return;
        setExporting(true);
        try {
            const blob = format === 'csv'
                ? await assessmentAPI.exportCSV(token, parseInt(id))
                : await assessmentAPI.exportPDF(token, parseInt(id));

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `assessment_${id}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error(`Failed to export ${format}:`, error);
        } finally {
            setExporting(false);
        }
    };

    const getMaturityColor = (level: string) => {
        const colors: Record<string, string> = {
            initial: 'text-red-600',
            developing: 'text-orange-600',
            defined: 'text-yellow-600',
            managed: 'text-blue-600',
            optimized: 'text-green-600',
        };
        return colors[level] || 'text-gray-600';
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600';
        if (score >= 60) return 'text-blue-600';
        if (score >= 40) return 'text-yellow-600';
        if (score >= 20) return 'text-orange-600';
        return 'text-red-600';
    };

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center">Loading report...</div>;
    }

    if (!summary) {
        return <div className="min-h-screen flex items-center justify-center">Report not found</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <button onClick={() => navigate('/dashboard')} className="text-primary-600 hover:text-primary-700">
                        ← Back to Dashboard
                    </button>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-6 flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800">{summary.assessment.title}</h1>
                        <p className="text-gray-600 mt-2">Assessment Report</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => handleExport('csv')}
                            disabled={exporting}
                            className="btn-secondary disabled:opacity-50"
                        >
                            Export CSV
                        </button>
                        <button
                            onClick={() => handleExport('pdf')}
                            disabled={exporting}
                            className="btn-primary disabled:opacity-50"
                        >
                            Export PDF
                        </button>
                    </div>
                </div>

                {/* Overall Score */}
                <div className="card mb-6 text-center">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">Overall Assessment</h2>
                    <div className={`text-6xl font-bold mb-2 ${getScoreColor(summary.overall_score)}`}>
                        {summary.overall_score}
                    </div>
                    <div className={`text-2xl font-semibold capitalize ${getMaturityColor(summary.overall_maturity)}`}>
                        {summary.overall_maturity} Maturity
                    </div>
                </div>

                {/* Category Scores */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    {Object.entries(summary.category_scores).map(([category, score]) => {
                        const result = summary.assessment.results.find((r) => r.category === category);
                        return (
                            <div key={category} className="card">
                                <h3 className="text-lg font-semibold text-gray-800 mb-2 capitalize">
                                    {category.replace('_', ' ')}
                                </h3>
                                <div className={`text-4xl font-bold mb-2 ${getScoreColor(score)}`}>
                                    {score}
                                </div>
                                {result && (
                                    <div className={`text-lg capitalize ${getMaturityColor(result.maturity_level)}`}>
                                        {result.maturity_level}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Recommendations */}
                <div className="card">
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">Recommendations</h2>
                    <div className="space-y-6">
                        {summary.assessment.results.map((result) => (
                            <div key={result.id} className="border-b border-gray-200 pb-4 last:border-0">
                                <h3 className="text-lg font-semibold text-gray-800 mb-2 capitalize">
                                    {result.category.replace('_', ' ')}
                                </h3>
                                <p className="text-gray-700">{result.recommendations}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ReportPage;
