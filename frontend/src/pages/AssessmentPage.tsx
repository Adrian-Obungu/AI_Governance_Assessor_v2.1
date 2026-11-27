import React, { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI } from '../services/api';
import { ApiError } from '../services/apiErrors';
import type { Assessment, AssessmentResult, Questionnaire, Question } from '../types';

const AssessmentPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [assessment, setAssessment] = useState<Assessment | null>(null);
    const [questionnaires, setQuestionnaires] = useState<Questionnaire[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [answers, setAnswers] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [notice, setNotice] = useState('');
    const { token, expireSession } = useAuth();
    const navigate = useNavigate();

    const loadData = useCallback(async (): Promise<Assessment | null> => {
        if (!token || !id) return null;
        try {
            const [assessmentData, questionnairesData] = await Promise.all([
                assessmentAPI.getAssessment(token, parseInt(id)),
                assessmentAPI.getQuestionnaires(),
            ]);
            setAssessment(assessmentData);
            setQuestionnaires(questionnairesData);

            // Select first incomplete category
            const completedCategories = assessmentData.results.map((result: AssessmentResult) => result.category);
            const firstIncomplete = questionnairesData.find(
                (q: Questionnaire) => !completedCategories.includes(q.category)
            );
            if (firstIncomplete) {
                setSelectedCategory(firstIncomplete.category);
            } else {
                setSelectedCategory(null);
            }
            return assessmentData;
        } catch (error) {
            console.error('Failed to load data:', error);
            if (error instanceof ApiError && error.kind === 'unauthorized') {
                expireSession();
                return null;
            }
            setError(error instanceof ApiError ? error.message : 'We could not load this assessment. Please refresh and try again.');
            return null;
        } finally {
            setLoading(false);
        }
    }, [id, token, expireSession]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleAnswerChange = (questionId: string, value: number) => {
        setAnswers({ ...answers, [questionId]: value });
    };

    const handleSubmit = async () => {
        if (!token || !id || !selectedCategory) return;
        setSubmitting(true);
        setError('');
        setNotice('');
        try {
            await assessmentAPI.submitAnswers(token, parseInt(id), selectedCategory, answers);
            setAnswers({});
            const refreshedAssessment = await loadData();
            if (refreshedAssessment?.status === 'completed') {
                navigate(`/report/${refreshedAssessment.id}`);
            } else {
                setNotice('Section saved. Continue with the next governance domain.');
            }
        } catch (error) {
            console.error('Failed to submit answers:', error);
            if (error instanceof ApiError && error.kind === 'unauthorized') {
                expireSession();
                return;
            }
            setError(error instanceof ApiError && error.kind === 'network'
                ? `${error.message} Your answers are still here.`
                : 'We could not save this section. Your answers are still here. Check your answers and try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const currentQuestionnaire = questionnaires.find((q) => q.category === selectedCategory);
    const completedCategories = assessment?.results.map((r) => r.category) || [];

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
    }

    if (!assessment) {
        return <div className="min-h-screen flex items-center justify-center">Assessment not found</div>;
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
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-800">{assessment.title}</h1>
                    {assessment.description && <p className="text-gray-600 mt-2">{assessment.description}</p>}
                    <p className="text-sm text-gray-600 mt-3" aria-live="polite">
                        {completedCategories.length} of {questionnaires.length} sections complete
                    </p>
                    {error && <div role="alert" className="mt-4 rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}
                    {notice && <div role="status" className="mt-4 rounded border border-green-200 bg-green-50 px-4 py-3 text-green-700">{notice}</div>}
                    <div className="mt-2 h-2 rounded-full bg-gray-200" role="progressbar" aria-valuemin={0} aria-valuemax={questionnaires.length} aria-valuenow={completedCategories.length} aria-label="Assessment progress">
                        <div className="h-2 rounded-full bg-primary-600 transition-all" style={{ width: `${questionnaires.length ? (completedCategories.length / questionnaires.length) * 100 : 0}%` }} />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Category selector */}
                    <div className="lg:col-span-1">
                        <div className="card sticky top-4">
                            <h3 className="font-semibold text-gray-800 mb-4">Categories</h3>
                            <div className="space-y-2">
                                {questionnaires.map((q) => {
                                    const isCompleted = completedCategories.includes(q.category);
                                    return (
                                        <button
                                            key={q.category}
                                            onClick={() => setSelectedCategory(q.category)}
                                            aria-current={selectedCategory === q.category ? 'step' : undefined}
                                            className={`w-full text-left px-4 py-2 rounded transition-colors ${selectedCategory === q.category
                                                ? 'bg-primary-600 text-white'
                                                : isCompleted
                                                    ? 'bg-green-100 text-green-800'
                                                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                                                }`}
                                        >
                                            {q.title}
                                            {isCompleted && <span className="ml-2">✓</span>}
                                        </button>
                                    );
                                })}
                                {assessment.status === 'completed' && (
                                    <button
                                        onClick={() => navigate(`/report/${assessment.id}`)}
                                        className="w-full btn-primary mt-4"
                                    >
                                        View Report
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Questionnaire */}
                    <div className="lg:col-span-3">
                        {currentQuestionnaire ? (
                            <div className="card">
                                <h2 className="text-2xl font-bold text-gray-800 mb-2">{currentQuestionnaire.title}</h2>
                                <p className="text-gray-600 mb-6">{currentQuestionnaire.description}</p>

                                <div className="space-y-6">
                                    {currentQuestionnaire.questions.map((question: Question) => (
                                        <fieldset key={question.id} className="border-b border-gray-200 pb-6 last:border-0">
                                            <legend className="font-medium text-gray-800 mb-3">{question.text}</legend>
                                            <div className="space-y-2">
                                                {question.options.map((option) => (
                                                    <label
                                                        key={option.value}
                                                        className="flex items-center p-3 border border-gray-300 rounded hover:bg-gray-50 cursor-pointer"
                                                    >
                                                        <input
                                                            type="radio"
                                                            name={question.id}
                                                            value={option.value}
                                                            checked={answers[question.id] === option.value}
                                                            onChange={() => handleAnswerChange(question.id, option.value)}
                                                            className="mr-3"
                                                        />
                                                        <span className="text-gray-700">{option.label}</span>
                                                    </label>
                                                ))}
                                            </div>
                                        </fieldset>
                                    ))}
                                </div>

                                <div className="mt-6">
                                    <button
                                        onClick={handleSubmit}
                                        disabled={submitting || Object.keys(answers).length !== currentQuestionnaire.questions.length}
                                        className="btn-primary disabled:opacity-50"
                                    >
                                        {submitting ? 'Saving section...' : completedCategories.length === questionnaires.length - 1 && !completedCategories.includes(currentQuestionnaire.category) ? 'Complete assessment' : 'Save and continue'}
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="card text-center py-12">
                                <p className="text-gray-600">Select a category to begin the assessment</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default AssessmentPage;
