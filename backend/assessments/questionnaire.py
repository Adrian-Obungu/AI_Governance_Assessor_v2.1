"""
AI Governance Assessment Questionnaire Templates
Defines questions and scoring for each assessment category
"""

from typing import Dict, List
from enum import Enum


class MaturityLevel(str, Enum):
    """Maturity levels based on CMMI framework"""
    INITIAL = "initial"
    DEVELOPING = "developing"
    DEFINED = "defined"
    MANAGED = "managed"
    OPTIMIZED = "optimized"


class AssessmentCategory(str, Enum):
    """Assessment categories"""
    DATA_PRIVACY = "data_privacy"
    MODEL_RISK = "model_risk"
    ETHICS = "ethics"
    COMPLIANCE = "compliance"


# Questionnaire templates for each category
QUESTIONNAIRES = {
    AssessmentCategory.DATA_PRIVACY: {
        "title": "Data Privacy Assessment",
        "description": "Evaluate data handling, privacy controls, and compliance with data protection regulations",
        "questions": [
            {
                "id": "dp_1",
                "text": "Does your organization have a documented data inventory for AI systems?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No inventory exists"},
                    {"value": 5, "label": "Partial inventory, not regularly updated"},
                    {"value": 10, "label": "Complete inventory, regularly maintained"}
                ]
            },
            {
                "id": "dp_2",
                "text": "Are data minimization principles applied to AI training data?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "Not considered"},
                    {"value": 5, "label": "Considered but not enforced"},
                    {"value": 10, "label": "Actively enforced with regular audits"}
                ]
            },
            {
                "id": "dp_3",
                "text": "Is personal data anonymized or pseudonymized before use in AI systems?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No anonymization"},
                    {"value": 7, "label": "Partial anonymization"},
                    {"value": 15, "label": "Full anonymization with validation"}
                ]
            },
            {
                "id": "dp_4",
                "text": "Are data retention and deletion policies defined and enforced?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No policies"},
                    {"value": 5, "label": "Policies exist but not enforced"},
                    {"value": 10, "label": "Policies enforced with automated controls"}
                ]
            },
            {
                "id": "dp_5",
                "text": "Is user consent obtained and managed for data used in AI?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No consent management"},
                    {"value": 7, "label": "Basic consent collection"},
                    {"value": 15, "label": "Comprehensive consent management with audit trail"}
                ]
            }
        ]
    },
    
    AssessmentCategory.MODEL_RISK: {
        "title": "Model Risk Assessment",
        "description": "Evaluate model development, validation, monitoring, and risk management practices",
        "questions": [
            {
                "id": "mr_1",
                "text": "Is there a formal model development lifecycle process?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No formal process"},
                    {"value": 7, "label": "Informal process, not documented"},
                    {"value": 15, "label": "Formal, documented, and enforced process"}
                ]
            },
            {
                "id": "mr_2",
                "text": "Are models validated before deployment?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No validation"},
                    {"value": 7, "label": "Basic validation by developers"},
                    {"value": 15, "label": "Independent validation with documented results"}
                ]
            },
            {
                "id": "mr_3",
                "text": "Is model performance monitored in production?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No monitoring"},
                    {"value": 7, "label": "Basic logging"},
                    {"value": 15, "label": "Comprehensive monitoring with alerting"}
                ]
            },
            {
                "id": "mr_4",
                "text": "Are model limitations and assumptions documented?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "Not documented"},
                    {"value": 5, "label": "Partially documented"},
                    {"value": 10, "label": "Fully documented and communicated"}
                ]
            },
            {
                "id": "mr_5",
                "text": "Is there a process for model retraining and updates?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No process"},
                    {"value": 5, "label": "Ad-hoc retraining"},
                    {"value": 10, "label": "Scheduled retraining with validation"}
                ]
            }
        ]
    },
    
    AssessmentCategory.ETHICS: {
        "title": "AI Ethics Assessment",
        "description": "Evaluate fairness, transparency, accountability, and ethical considerations",
        "questions": [
            {
                "id": "eth_1",
                "text": "Are AI systems tested for bias and fairness?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No testing"},
                    {"value": 7, "label": "Basic testing during development"},
                    {"value": 15, "label": "Comprehensive testing with ongoing monitoring"}
                ]
            },
            {
                "id": "eth_2",
                "text": "Is there transparency about AI system decisions?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No transparency"},
                    {"value": 7, "label": "Limited explanations available"},
                    {"value": 15, "label": "Full explainability and documentation"}
                ]
            },
            {
                "id": "eth_3",
                "text": "Are there human oversight mechanisms for AI decisions?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "Fully automated, no oversight"},
                    {"value": 7, "label": "Human review for some decisions"},
                    {"value": 15, "label": "Human-in-the-loop for critical decisions"}
                ]
            },
            {
                "id": "eth_4",
                "text": "Is there an AI ethics review board or committee?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No ethics review"},
                    {"value": 5, "label": "Informal review process"},
                    {"value": 10, "label": "Formal ethics board with regular reviews"}
                ]
            },
            {
                "id": "eth_5",
                "text": "Are stakeholders consulted about AI system impacts?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No stakeholder engagement"},
                    {"value": 5, "label": "Limited consultation"},
                    {"value": 10, "label": "Regular stakeholder engagement and feedback"}
                ]
            }
        ]
    },
    
    AssessmentCategory.COMPLIANCE: {
        "title": "Regulatory Compliance Assessment",
        "description": "Evaluate compliance with AI regulations, standards, and legal requirements",
        "questions": [
            {
                "id": "comp_1",
                "text": "Are relevant AI regulations and standards identified?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "Not identified"},
                    {"value": 5, "label": "Partially identified"},
                    {"value": 10, "label": "Comprehensive regulatory mapping"}
                ]
            },
            {
                "id": "comp_2",
                "text": "Is there a compliance management program for AI?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No program"},
                    {"value": 7, "label": "Basic compliance tracking"},
                    {"value": 15, "label": "Comprehensive program with regular audits"}
                ]
            },
            {
                "id": "comp_3",
                "text": "Are AI systems documented for regulatory requirements?",
                "weight": 15,
                "options": [
                    {"value": 0, "label": "No documentation"},
                    {"value": 7, "label": "Basic documentation"},
                    {"value": 15, "label": "Complete documentation meeting all requirements"}
                ]
            },
            {
                "id": "comp_4",
                "text": "Are there processes for responding to regulatory inquiries?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No process"},
                    {"value": 5, "label": "Ad-hoc responses"},
                    {"value": 10, "label": "Formal process with designated owners"}
                ]
            },
            {
                "id": "comp_5",
                "text": "Is compliance training provided to AI teams?",
                "weight": 10,
                "options": [
                    {"value": 0, "label": "No training"},
                    {"value": 5, "label": "One-time training"},
                    {"value": 10, "label": "Regular, updated training programs"}
                ]
            }
        ]
    }
}


def calculate_category_score(answers: Dict[str, int], category: AssessmentCategory) -> int:
    """Calculate score for a category based on answers"""
    questionnaire = QUESTIONNAIRES[category]
    total_weight = sum(q["weight"] for q in questionnaire["questions"])
    
    score = 0
    for question in questionnaire["questions"]:
        answer_value = answers.get(question["id"], 0)
        score += answer_value
    
    # Normalize to 0-100
    return int((score / total_weight) * 100) if total_weight > 0 else 0


def get_maturity_level(score: int) -> MaturityLevel:
    """Determine maturity level based on score"""
    if score < 20:
        return MaturityLevel.INITIAL
    elif score < 40:
        return MaturityLevel.DEVELOPING
    elif score < 60:
        return MaturityLevel.DEFINED
    elif score < 80:
        return MaturityLevel.MANAGED
    else:
        return MaturityLevel.OPTIMIZED


def get_recommendations(category: AssessmentCategory, score: int, maturity: MaturityLevel) -> str:
    """Generate recommendations based on assessment results"""
    recommendations = {
        AssessmentCategory.DATA_PRIVACY: {
            MaturityLevel.INITIAL: "Establish basic data inventory and privacy policies. Implement data classification and access controls.",
            MaturityLevel.DEVELOPING: "Enhance data anonymization techniques. Implement comprehensive consent management.",
            MaturityLevel.DEFINED: "Automate privacy controls. Conduct regular privacy impact assessments.",
            MaturityLevel.MANAGED: "Implement privacy-by-design principles. Enhance data minimization practices.",
            MaturityLevel.OPTIMIZED: "Maintain excellence. Share best practices across organization."
        },
        AssessmentCategory.MODEL_RISK: {
            MaturityLevel.INITIAL: "Establish model development standards. Implement basic validation processes.",
            MaturityLevel.DEVELOPING: "Create formal model governance framework. Implement model monitoring.",
            MaturityLevel.DEFINED: "Enhance validation with independent review. Implement automated monitoring.",
            MaturityLevel.MANAGED: "Implement advanced model risk management. Enhance retraining processes.",
            MaturityLevel.OPTIMIZED: "Maintain excellence. Continuously improve model governance."
        },
        AssessmentCategory.ETHICS: {
            MaturityLevel.INITIAL: "Establish AI ethics principles. Implement basic bias testing.",
            MaturityLevel.DEVELOPING: "Create ethics review process. Enhance transparency mechanisms.",
            MaturityLevel.DEFINED: "Establish ethics board. Implement comprehensive fairness testing.",
            MaturityLevel.MANAGED: "Enhance stakeholder engagement. Implement advanced explainability.",
            MaturityLevel.OPTIMIZED: "Maintain excellence. Lead industry in ethical AI practices."
        },
        AssessmentCategory.COMPLIANCE: {
            MaturityLevel.INITIAL: "Identify applicable regulations. Establish basic compliance tracking.",
            MaturityLevel.DEVELOPING: "Create compliance management program. Enhance documentation.",
            MaturityLevel.DEFINED: "Implement automated compliance monitoring. Conduct regular audits.",
            MaturityLevel.MANAGED: "Enhance regulatory engagement. Implement proactive compliance.",
            MaturityLevel.OPTIMIZED: "Maintain excellence. Lead industry in AI compliance."
        }
    }
    
    return recommendations.get(category, {}).get(maturity, "Continue improving governance practices.")
