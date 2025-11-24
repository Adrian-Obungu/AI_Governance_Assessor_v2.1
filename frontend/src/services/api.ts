// API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Auth endpoints
export const authAPI = {
    signup: async (email: string, password: string, fullName?: string) => {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Signup failed');
        }
        return response.json();
    },

    login: async (email: string, password: string) => {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        return response.json();
    },

    requestPasswordReset: async (email: string) => {
        const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        if (!response.ok) throw new Error('Password reset request failed');
        return response.json();
    },
};

// Assessment endpoints
export const assessmentAPI = {
    getQuestionnaires: async () => {
        const response = await fetch(`${API_BASE_URL}/assessments/questionnaires`);
        if (!response.ok) throw new Error('Failed to fetch questionnaires');
        return response.json();
    },

    createAssessment: async (token: string, title: string, description?: string) => {
        const response = await fetch(`${API_BASE_URL}/assessments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ title, description }),
        });
        if (!response.ok) throw new Error('Failed to create assessment');
        return response.json();
    },

    listAssessments: async (token: string) => {
        const response = await fetch(`${API_BASE_URL}/assessments`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch assessments');
        return response.json();
    },

    getAssessment: async (token: string, id: number) => {
        const response = await fetch(`${API_BASE_URL}/assessments/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch assessment');
        return response.json();
    },

    submitAnswers: async (token: string, assessmentId: number, category: string, answers: Record<string, number>) => {
        const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}/answers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ category, answers }),
        });
        if (!response.ok) throw new Error('Failed to submit answers');
        return response.json();
    },

    getSummary: async (token: string, assessmentId: number) => {
        const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}/summary`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to fetch summary');
        return response.json();
    },

    exportCSV: async (token: string, assessmentId: number) => {
        const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}/export/csv`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to export CSV');
        return response.blob();
    },

    exportPDF: async (token: string, assessmentId: number) => {
        const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}/export/pdf`, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Failed to export PDF');
        return response.blob();
    },
};
