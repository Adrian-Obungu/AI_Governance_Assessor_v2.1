import { expect, test, type Page, type Route } from '@playwright/test';

const system = {
  id: 1,
  user_id: 1,
  name: 'Synthetic customer support assistant',
  purpose: 'Answers fabricated customer questions using an approved synthetic knowledge base.',
  department: 'Customer Operations',
  business_owner: 'Customer Operations Team',
  provider: 'Synthetic Internal Prototype',
  lifecycle_stage: 'pilot',
  geographies: ['Kenya', 'Uganda'],
  data_categories: ['Synthetic customer messages'],
  affected_groups: ['Synthetic customers', 'support staff'],
  review_date: '2099-12-31',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const assessment = {
  id: 1,
  user_id: 1,
  ai_system_id: 1,
  title: 'Synthetic customer support baseline',
  description: 'Synthetic assessment for Playwright governance workflow coverage.',
  schema_version: '1.0',
  status: 'completed',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  completed_at: '2026-01-01T00:00:00Z',
  results: [],
};

function evidenceRecord() {
  return {
    id: 1,
    user_id: 1,
    ai_system_id: 1,
    assessment_id: 1,
    title: 'Synthetic customer data handling policy',
    description: 'Synthetic metadata record describing the documented handling process.',
    evidence_type: 'policy',
    source_location: 'Internal synthetic reference GOV-AI-001',
    owner: 'Customer Operations Team',
    collected_on: '2026-01-01',
    review_date: '2099-12-31',
    status: 'submitted',
    reviewer_notes: 'Synthetic metadata-only test record.',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

function findingRecord() {
  return {
    id: 1,
    user_id: 1,
    ai_system_id: 1,
    assessment_id: 1,
    evidence_id: 1,
    title: 'Synthetic review owner gap',
    conclusion: 'The synthetic policy does not identify a named periodic review owner.',
    priority: 'high',
    owner: 'Customer Operations Team',
    due_date: '2099-12-31',
    remediation_action: 'Assign a named review owner in the synthetic policy.',
    status: 'open',
    reviewer_notes: 'Synthetic finding for browser validation.',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

function reviewRecord() {
  return {
    id: 1,
    user_id: 1,
    ai_system_id: 1,
    assessment_id: 1,
    reassessment_id: null,
    reviewer: 'Synthetic Governance Lead',
    review_date: '2026-01-01',
    decision: 'continue',
    next_review_date: '2099-12-31',
    material_change: false,
    change_summary: null,
    reviewer_notes: 'Synthetic human review record.',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

function signalRecord(status = 'new') {
  return {
    id: 1,
    user_id: 1,
    ai_system_id: 1,
    finding_id: null,
    review_id: 1,
    signal_type: 'feedback',
    severity: 'medium',
    status,
    title: 'Synthetic request for clearer explanations',
    description: 'Synthetic support feedback requested clearer explanations.',
    reported_on: '2026-01-01',
    reported_by: 'Synthetic Support Team',
    owner: 'AI Operations',
    response_action: 'Discuss the feedback during the next human review.',
    reviewer_notes: 'Synthetic feedback record.',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

async function installGovernanceMock(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'governance-mock-token');
    localStorage.setItem('auth_email', 'governance-playwright@example.com');
  });

  let systems: typeof system[] = [];
  let evidence: ReturnType<typeof evidenceRecord>[] = [];
  let findings: ReturnType<typeof findingRecord>[] = [];
  let reviews: ReturnType<typeof reviewRecord>[] = [];
  let signals: ReturnType<typeof signalRecord>[] = [];

  const respond = async (route: Route, body: unknown, status = 200) => {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
  };

  await page.route('**/api/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace(/^\/api/, '');
    const method = request.method();

    if (path === '/inventory' && method === 'GET') return respond(route, systems);
    if (path === '/inventory' && method === 'POST') {
      systems = [system];
      return respond(route, system, 201);
    }
    if (path === '/assessments' && method === 'GET') return respond(route, [assessment]);
    if (path === '/assessments/questionnaires' && method === 'GET') return respond(route, []);
    if (path === '/evidence' && method === 'GET') return respond(route, evidence);
    if (path === '/evidence' && method === 'POST') {
      evidence = [evidenceRecord()];
      return respond(route, evidence[0], 201);
    }
    if (path === '/findings' && method === 'GET') return respond(route, findings);
    if (path === '/findings' && method === 'POST') {
      findings = [findingRecord()];
      return respond(route, findings[0], 201);
    }
    if (path === '/reviews' && method === 'GET') return respond(route, reviews);
    if (path === '/reviews' && method === 'POST') {
      reviews = [reviewRecord()];
      return respond(route, reviews[0], 201);
    }
    if (path === '/signals' && method === 'GET') return respond(route, signals);
    if (path === '/signals' && method === 'POST') {
      signals = [signalRecord()];
      return respond(route, signals[0], 201);
    }
    if (path === '/signals/1' && method === 'PUT') {
      signals = [signalRecord('closed')];
      return respond(route, signals[0]);
    }
    if (path === '/activity' && method === 'GET') {
      return respond(route, [
        { source_type: 'inventory', source_id: 1, occurred_at: '2026-01-01T06:00:00Z', title: system.name, summary: 'AI system context recorded.', status: 'pilot' },
        { source_type: 'assessment', source_id: 1, occurred_at: '2026-01-01T07:00:00Z', title: assessment.title, summary: 'Assessment completed.', status: 'completed' },
        { source_type: 'evidence', source_id: 1, occurred_at: '2026-01-01T08:00:00Z', title: evidenceRecord().title, summary: 'Evidence metadata recorded.', status: 'submitted' },
        { source_type: 'finding', source_id: 1, occurred_at: '2026-01-01T09:00:00Z', title: findingRecord().title, summary: 'Owned remediation gap recorded.', status: 'open', priority: 'high' },
        { source_type: 'review', source_id: 1, occurred_at: '2026-01-01T10:00:00Z', title: reviewRecord().reviewer, summary: 'Human review recorded.', status: 'continue' },
        { source_type: 'signal', source_id: 1, occurred_at: '2026-01-01T11:00:00Z', title: signalRecord().title, summary: 'Operational feedback recorded.', status: 'new', severity: 'medium' },
      ]);
    }
    if (path === '/governance/snapshots' && method === 'GET') {
      return respond(route, [{
        ai_system_id: 1,
        system_name: system.name,
        lifecycle_stage: system.lifecycle_stage,
        review_date: system.review_date,
        review_due: false,
        coverage: { assessments: 1, evidence_records: 1, findings: 1, human_reviews: 1, operational_signals: 1 },
        open_findings: 1,
        active_signals: 1,
        attention: [{ level: 'attention', source_type: 'finding', source_id: 1, title: findingRecord().title, detail: 'Assign and track the synthetic remediation action.' }],
        next_action: 'Review the open finding with the assigned owner.',
      }]);
    }

    return respond(route, { detail: `Unhandled mocked endpoint: ${method} ${path}` }, 404);
  });
}

async function capture(page: Page, name: string) {
  if (process.env.E2E_EVIDENCE !== '1') return;
  await page.screenshot({ path: `test-results/governance-${name}.png`, fullPage: true });
}

test.describe('context-first governance workflow', () => {
  test('records context, evidence, remediation, review, signals, activity, and snapshot', async ({ page }) => {
    await installGovernanceMock(page);

    await test.step('dashboard exposes the governance workflow', async () => {
      await page.goto('/dashboard', { waitUntil: 'networkidle' });
      await expect(page.getByRole('button', { name: 'Open AI-system inventory' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Open evidence register' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Open findings' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Open reviews' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Open signals' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Open activity' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Open snapshot' })).toBeVisible();
      await capture(page, '01-dashboard-workflow-links');
    });

    await test.step('creates an AI-system context record', async () => {
      await page.getByRole('button', { name: 'Open AI-system inventory' }).click();
      await expect(page).toHaveURL(/\/inventory$/);
      await page.getByRole('button', { name: '+ Add AI system' }).click();
      const dialog = page.getByRole('dialog');
      await dialog.getByLabel('What is it called?').fill(system.name);
      await dialog.getByLabel('What does it do?').fill(system.purpose);
      await dialog.getByLabel('Department').fill(system.department);
      await dialog.getByLabel('Business owner').fill(system.business_owner);
      await dialog.getByLabel('Provider or vendor').fill(system.provider);
      await dialog.getByLabel('Where is it now?').selectOption('pilot');
      await dialog.getByLabel('Where is it used?').fill('Kenya, Uganda');
      await dialog.getByLabel('What data does it use?').fill('Synthetic customer messages');
      await dialog.getByLabel('Who may be affected?').fill('Synthetic customers, support staff');
      await dialog.getByLabel('When should it be reviewed next?').fill(system.review_date);
      await dialog.getByRole('button', { name: 'Save AI system' }).click();
      await expect(page.getByRole('heading', { name: system.name })).toBeVisible();
      await capture(page, '02-inventory-created');
    });

    await test.step('records metadata-only evidence', async () => {
      await page.goto('/evidence', { waitUntil: 'networkidle' });
      await page.getByRole('button', { name: '+ Add evidence record' }).click();
      const dialog = page.getByRole('dialog');
      await dialog.getByLabel('AI system').selectOption('1');
      await dialog.getByLabel('Assessment (optional)').selectOption('1');
      await dialog.getByLabel('Evidence title').fill(evidenceRecord().title);
      await dialog.getByLabel('What does it show?').fill(evidenceRecord().description);
      await dialog.getByLabel('Evidence type').selectOption('policy');
      await dialog.getByLabel('Status').selectOption('submitted');
      await dialog.getByLabel('Evidence owner').fill(evidenceRecord().owner);
      await dialog.getByLabel('Source location').fill(evidenceRecord().source_location);
      await dialog.getByLabel('Collected on').fill('2026-01-01');
      await dialog.getByLabel('Review date').fill('2099-12-31');
      await dialog.getByRole('button', { name: 'Save evidence record' }).click();
      await expect(page.getByRole('heading', { name: evidenceRecord().title })).toBeVisible();
      await expect(page.getByText(/no files are uploaded/i)).toBeVisible();
      await capture(page, '03-evidence-created');
    });

    await test.step('creates an owned finding', async () => {
      await page.goto('/findings', { waitUntil: 'networkidle' });
      await page.getByRole('button', { name: '+ Add finding' }).click();
      const dialog = page.getByRole('dialog');
      await dialog.getByLabel('AI system').selectOption('1');
      await dialog.getByLabel('Supporting evidence').selectOption('1');
      await dialog.getByLabel('Assessment (optional)').selectOption('1');
      await dialog.getByLabel('Finding title').fill(findingRecord().title);
      await dialog.getByLabel('What did you observe?').fill(findingRecord().conclusion);
      await dialog.getByLabel('Priority').selectOption('high');
      await dialog.getByLabel('Action owner').fill(findingRecord().owner);
      await dialog.getByLabel('Due date').fill(findingRecord().due_date);
      await dialog.getByLabel('Remediation action').fill(findingRecord().remediation_action);
      await dialog.getByLabel('Status').selectOption('open');
      await dialog.getByRole('button', { name: 'Save finding' }).click();
      await expect(page.getByRole('heading', { name: findingRecord().title })).toBeVisible();
      await capture(page, '04-finding-created');
    });

    await test.step('records a human review', async () => {
      await page.goto('/reviews', { waitUntil: 'networkidle' });
      await page.getByRole('button', { name: '+ Add review' }).click();
      const dialog = page.getByRole('dialog');
      await dialog.getByLabel('AI system').selectOption('1');
      await dialog.getByRole('textbox', { name: 'Reviewer', exact: true }).fill(reviewRecord().reviewer);
      await dialog.getByLabel('Assessment reviewed').selectOption('1');
      await dialog.getByRole('textbox', { name: 'Review date', exact: true }).fill('2026-01-01');
      await dialog.getByLabel('Decision').selectOption('continue');
      await dialog.getByLabel('Next review date').fill('2099-12-31');
      await dialog.getByLabel('Reviewer notes (optional)').fill(reviewRecord().reviewer_notes);
      await dialog.getByRole('button', { name: 'Save review' }).click();
      await expect(page.getByRole('heading', { name: reviewRecord().reviewer })).toBeVisible();
      await capture(page, '05-review-created');
    });

    await test.step('records and closes an operational signal', async () => {
      await page.goto('/signals', { waitUntil: 'networkidle' });
      await page.getByRole('button', { name: '+ Add signal' }).click();
      const form = page.locator('form').filter({ hasText: 'Add an operational signal' });
      await form.locator('select').nth(0).selectOption('1');
      await form.locator('select').nth(1).selectOption('feedback');
      await form.locator('select').nth(2).selectOption('medium');
      await form.locator('input').nth(0).fill('2026-01-01');
      await form.locator('input').nth(1).fill(signalRecord().title);
      await form.locator('textarea').nth(0).fill(signalRecord().description);
      await form.locator('input').nth(2).fill(signalRecord().reported_by);
      await form.locator('input').nth(3).fill(signalRecord().owner);
      await form.locator('textarea').nth(1).fill(signalRecord().response_action);
      await form.getByRole('button', { name: 'Save signal' }).click();
      await expect(page.getByRole('heading', { name: signalRecord().title })).toBeVisible();
      await page.getByRole('button', { name: 'Mark closed' }).click();
      await expect(page.getByText('closed', { exact: true })).toBeVisible();
      await capture(page, '06-signal-closed');
    });

    await test.step('shows the consolidated activity timeline', async () => {
      await page.goto('/activity', { waitUntil: 'networkidle' });
      await expect(page.getByRole('heading', { name: 'Governance activity' })).toBeVisible();
      for (const label of ['Synthetic customer support assistant', 'Synthetic customer support baseline', 'Synthetic customer data handling policy', 'Synthetic review owner gap', 'Synthetic Governance Lead', 'Synthetic request for clearer explanations']) {
        await expect(page.getByRole('heading', { name: label, exact: true })).toBeVisible();
      }
      await page.getByLabel('Activity type').selectOption('finding');
      await expect(page.getByText('Synthetic review owner gap', { exact: true })).toBeVisible();
      await capture(page, '07-activity-filtered');
    });

    await test.step('shows the governance snapshot and human next action', async () => {
      await page.goto('/snapshot', { waitUntil: 'networkidle' });
      await page.getByLabel('AI system').selectOption('1');
      await expect(page.getByRole('heading', { name: 'AI-system governance snapshot' })).toBeVisible();
      await expect(page.getByRole('heading', { name: system.name })).toBeVisible();
      await expect(page.getByText('Next human action', { exact: true })).toBeVisible();
      await expect(page.getByText('Review the open finding with the assigned owner.', { exact: true })).toBeVisible();
      await expect(page.getByText('Open finding', { exact: true })).toBeVisible();
      await capture(page, '08-governance-snapshot');
    });
  });
});
