import type { Page, Route } from '@playwright/test';

let assessmentTitle = 'Mock governance assessment';
let assessmentDescription: string | null = 'Mocked API assessment';

const categories = [
  {
    category: 'data_privacy',
    title: 'Data Privacy Assessment',
    description: 'Evaluate data handling and privacy controls.',
    question: { id: 'dp_1', text: 'Is there a documented data inventory?', weight: 10, options: [{ value: 0, label: 'No' }, { value: 10, label: 'Yes' }] },
  },
  {
    category: 'model_risk',
    title: 'Model Risk Assessment',
    description: 'Evaluate model development and monitoring.',
    question: { id: 'mr_1', text: 'Are models validated before deployment?', weight: 10, options: [{ value: 0, label: 'No' }, { value: 10, label: 'Yes' }] },
  },
  {
    category: 'ethics',
    title: 'AI Ethics Assessment',
    description: 'Evaluate fairness, transparency, and accountability.',
    question: { id: 'eth_1', text: 'Are AI systems tested for bias?', weight: 10, options: [{ value: 0, label: 'No' }, { value: 10, label: 'Yes' }] },
  },
  {
    category: 'compliance',
    title: 'Regulatory Compliance Assessment',
    description: 'Evaluate compliance with AI regulations and standards.',
    question: { id: 'comp_1', text: 'Are relevant regulations identified?', weight: 10, options: [{ value: 0, label: 'No' }, { value: 10, label: 'Yes' }] },
  },
];

function makeAssessment(results: Array<Record<string, unknown>> = []) {
  return {
    id: 1,
    user_id: 1,
    title: assessmentTitle,
    description: assessmentDescription,
    schema_version: '1.0',
    status: results.length === categories.length ? 'completed' : results.length ? 'in_progress' : 'draft',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    completed_at: results.length === categories.length ? '2026-01-01T00:00:00Z' : null,
    results,
  };
}

export async function installMockApi(page: Page, options: { seedCompletedCategories?: number } = {}) {
  await page.addInitScript(() => {
    if (localStorage.getItem('mock_logged_out') !== '1') {
      if (!localStorage.getItem('auth_token')) localStorage.setItem('auth_token', 'mock-token');
      if (!localStorage.getItem('auth_email')) localStorage.setItem('auth_email', 'mock@example.com');
    }
  });
  assessmentTitle = 'Mock governance assessment';
  assessmentDescription = 'Mocked API assessment';
  const results: Array<Record<string, unknown>> = categories.slice(0, options.seedCompletedCategories ?? 0).map((item, index) => ({
    id: index + 1,
    assessment_id: 1,
    category: item.category,
    score: 100,
    maturity_level: 'optimized',
    recommendations: 'Continue improving governance practices.',
    created_at: '2026-01-01T00:00:00Z',
  }));

  const respond = async (route: Route, body: unknown, status = 200, contentType = 'application/json') => {
    await route.fulfill({ status, contentType, body: contentType === 'application/json' ? JSON.stringify(body) : String(body) });
  };

  await page.route('**/api/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace(/^\/api/, '');
    const method = request.method();

    if (path === '/auth/signup' && method === 'POST') return respond(route, { access_token: 'mock-token' });
    if (path === '/auth/login' && method === 'POST') return respond(route, { access_token: 'mock-token' });
    if (path === '/auth/reset-password' && method === 'POST') return respond(route, { message: 'ok' });
    if (path === '/assessments/questionnaires' && method === 'GET') {
      return respond(route, categories.map(({ question, ...category }) => ({ ...category, questions: [question] })));
    }
    if (path === '/assessments' && method === 'GET') return respond(route, [makeAssessment(results)]);
    if (path === '/assessments' && method === 'POST') {
      const payload = JSON.parse(request.postData() || '{}') as { title?: string; description?: string };
      const assessment = makeAssessment(results);
      assessmentTitle = payload.title || assessmentTitle;
      assessmentDescription = payload.description || null;
      assessment.title = assessmentTitle;
      assessment.description = assessmentDescription;
      return respond(route, assessment, 201);
    }
    if (path === '/assessments/1' && method === 'GET') return respond(route, makeAssessment(results));
    if (path === '/assessments/1/answers' && method === 'POST') {
      const payload = JSON.parse(request.postData() || '{}') as { category: string; answers: Record<string, number> };
      const categoryIndex = categories.findIndex((item) => item.category === payload.category);
      const existing = results.find((result) => result.category === payload.category);
      const result = {
        id: existing?.id || results.length + 1,
        assessment_id: 1,
        category: payload.category,
        score: 100,
        maturity_level: 'optimized',
        recommendations: 'Continue improving governance practices.',
        created_at: '2026-01-01T00:00:00Z',
      };
      if (existing) Object.assign(existing, result);
      else results.push(result);
      if (categoryIndex < 0) return respond(route, { detail: 'Unknown category' }, 422);
      return respond(route, result);
    }
    if (path === '/assessments/1/summary' && method === 'GET') {
      return respond(route, {
        assessment: makeAssessment(results),
        overall_score: results.length ? 100 : 0,
        overall_maturity: results.length ? 'optimized' : 'initial',
        category_scores: Object.fromEntries(results.map((result) => [result.category, result.score])),
      });
    }
    if (path === '/assessments/1/export/csv' && method === 'GET') return respond(route, 'category,score\ndata_privacy,100\n', 200, 'text/csv');
    if (path === '/assessments/1/export/pdf' && method === 'GET') return respond(route, '%PDF-1.4 mock', 200, 'application/pdf');

    return respond(route, { detail: 'Mock endpoint not found' }, 404);
  });
}
