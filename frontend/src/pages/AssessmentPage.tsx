import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI } from '../services/api';
import type { Assessment, Questionnaire, Question } from '../types';

const AssessmentPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [assessment, setAssessment] = useState<Assessment | null>(null);
    const [questionnaires, setQuestionnaires] = useState<Questionnaire[]>([]);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [answers, setAnswers] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        loadData();
    }, [id]);

    const loadData = async () => {
        if (!token || !id) return;
        try {
            const [assessmentData, questionnairesData] = await Promise.all([
                assessmentAPI.getAssessment(token, parseInt(id)),
                assessmentAPI.getQuestionnaires(),
            ]);
            setAssessment(assessmentData);
            setQuestionnaires(questionnairesData);

            // Select first incomplete category
            const completedCategories = assessmentData.results.map((r: any) => r.category);
            const firstIncomplete = questionnairesData.find(
                (q: Questionnaire) => !completedCategories.includes(q.category)
            );
            if (firstIncomplete) {
                setSelectedCategory(firstIncomplete.category);
            }
        } catch (error) {
            console.error('Failed to load data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerChange = (questionId: string, value: number) => {
        setAnswers({ ...answers, [questionId]: value });
    };

    const handleSubmit = async () => {
        if (!token || !id || !selectedCategory) return;
        try {
            await assessmentAPI.submitAnswers(token, parseInt(id), selectedCategory, answers);
            setAnswers({});
            loadData();
        } catch (error) {
            console.error('Failed to submit answers:', error);
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
                                        <div key={question.id} className="border-b border-gray-200 pb-6 last:border-0">
                                            <h4 className="font-medium text-gray-800 mb-3">{question.text}</h4>
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
                                        </div>
                                    ))}
                                </div>

                                <div className="mt-6">
                                    <button
                                        onClick={handleSubmit}
                                        disabled={Object.keys(answers).length !== currentQuestionnaire.questions.length}
                                        className="btn-primary disabled:opacity-50"
                                    >
                                        Submit Answers
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
