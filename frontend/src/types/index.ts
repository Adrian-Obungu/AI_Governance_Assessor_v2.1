export interface User {
    id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
    created_at: string;
}

export interface Assessment {
    id: number;
    user_id: number;
    title: string;
    description?: string;
    schema_version: string;
    status: 'draft' | 'in_progress' | 'completed';
    created_at: string;
    updated_at: string;
    completed_at?: string;
    results: AssessmentResult[];
}

export interface AssessmentResult {
    id: number;
    assessment_id: number;
    category: string;
    score: number;
    maturity_level: string;
    recommendations?: string;
    created_at: string;
}

export interface Question {
    id: string;
    text: string;
    weight: number;
    options: {
        value: number;
        label: string;
    }[];
}

export interface Questionnaire {
    category: string;
    title: string;
    description: string;
    questions: Question[];
}

export interface AssessmentSummary {
    assessment: Assessment;
    overall_score: number;
    overall_maturity: string;
    category_scores: Record<string, number>;
}
