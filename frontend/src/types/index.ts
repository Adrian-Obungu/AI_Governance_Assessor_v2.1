export interface User {
    id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
    created_at: string;
}

export type AISystemLifecycle = 'discovery' | 'pilot' | 'in_production' | 'retired';

export interface AISystem {
    id: number;
    user_id: number;
    name: string;
    purpose: string;
    department?: string;
    business_owner?: string;
    provider?: string;
    lifecycle_stage: AISystemLifecycle;
    geographies: string[];
    data_categories: string[];
    affected_groups: string[];
    review_date?: string;
    created_at: string;
    updated_at: string;
}

export interface Assessment {
    id: number;
    user_id: number;
    ai_system_id?: number;
    ai_system?: Pick<AISystem, 'id' | 'name' | 'purpose'>;
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

export type EvidenceType = 'policy' | 'procedure' | 'contract' | 'technical_document' | 'training_record' | 'audit_record' | 'review_note' | 'other';
export type EvidenceStatus = 'draft' | 'submitted' | 'reviewed' | 'needs_update';

export interface EvidenceRecord {
    id: number;
    user_id: number;
    ai_system_id: number;
    assessment_id?: number;
    title: string;
    description: string;
    evidence_type: EvidenceType;
    source_location?: string;
    owner?: string;
    collected_on?: string;
    review_date?: string;
    status: EvidenceStatus;
    reviewer_notes?: string;
    created_at: string;
    updated_at: string;
}

export type FindingPriority = 'low' | 'medium' | 'high' | 'critical';
export type FindingStatus = 'open' | 'in_progress' | 'resolved' | 'accepted_risk';

export interface FindingRecord {
    id: number;
    user_id: number;
    ai_system_id: number;
    evidence_id: number;
    assessment_id?: number;
    title: string;
    conclusion: string;
    priority: FindingPriority;
    owner: string;
    remediation_action: string;
    due_date?: string;
    status: FindingStatus;
    reviewer_notes?: string;
    created_at: string;
    updated_at: string;
}
