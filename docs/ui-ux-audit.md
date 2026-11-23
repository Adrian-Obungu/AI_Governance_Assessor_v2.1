# AI Governance Assessor UI/UX audit

## Scope and current evidence

This audit covers the frontend source, the production build, the Docker-served application behavior reported from Windows, and a rendered login preview of the same codebase. The Windows logs confirm that PostgreSQL, the backend, Nginx, and the `/api/health` proxy are working. They do not provide browser console output or a complete authenticated journey, so the assessment workflow and report screen still need a user-session walkthrough with synthetic data.

The original black-and-white appearance had a technical cause rather than only a visual-design problem. The built CSS contained literal `@tailwind` and `@apply` directives because the repository had no PostCSS configuration while using a Tailwind directive-based stylesheet. The frontend therefore served HTML and JavaScript, but most intended utility and component styling was never generated. This has now been corrected by adding the PostCSS configuration, pinning the compatible Tailwind 3 toolchain, and replacing the dark browser-default root styling with a light visual system.

A second runtime issue was also found during the audit. The production entry point rendered `App` without a `BrowserRouter`, even though the application uses React Router routes. The entry point now mounts `App` inside `BrowserRouter`. Frontend tests and the production build pass after both fixes.

## Current UX assessment

The current interface is a functional prototype, not yet a polished governance product. Its strengths are a short authentication flow, a clear route structure, a simple assessment-to-report journey, and a small number of primary actions. The code is also compact enough to improve without a large migration.

The main weakness is that the interface currently exposes implementation structure rather than a user-centred assessment model. The dashboard is mostly a list of cards. The assessment page presents categories and a full question set, but does not visibly communicate overall progress, time remaining, saved state, question purpose, or what a score means. The report presents scores and recommendations but does not yet explain evidence, confidence, priority, ownership, or the next action. These gaps increase uncertainty and force users to remember what they have already done.

The login page is visually sparse and has no product context beyond the name. It should explain the outcome of the service in one sentence, distinguish sign-in from registration more clearly, show password requirements before submission, and present errors beside the relevant fields. Several labels are not explicitly associated with input IDs, which should be corrected for assistive technology. The dashboard’s clickable assessment cards are `div` elements rather than links or keyboard-operable controls. The modal should expose dialog semantics, focus management, and an explicit close action.

The assessment flow has the largest cognitive-load risk. Four categories are shown in a side panel, while all questions in the selected category appear together. This is workable for a short questionnaire but will become tiring as question count grows. The form should use a question protocol: each question must have a documented decision purpose, audience, answer validation rule, and downstream use. Irrelevant questions should be removed or branched away. GOV.UK recommends beginning with one thing per page and using branching so users answer only relevant questions.[2]

The application should not make the overall score the only explanation of risk. NIST’s AI Risk Management Framework is organized around Govern, Map, Measure, and Manage; the product should make those stages visible in the assessment structure and report narrative instead of presenting an unexplained maturity label.[6]

## Design specification for the next iteration

The recommended product direction is a calm, evidence-led enterprise assessment interface: light neutral surfaces, deep navy text, one confident blue signature action color, restrained amber/red/green status colors, generous spacing, and short explanatory copy. The interface should feel serious and trustworthy without becoming visually heavy. Decorative imagery is not necessary for this internal governance workflow.

The minimum accessibility target should be WCAG 2.2 AA. WCAG 2.2 specifically adds guidance relevant here, including focus visibility, target size, consistent help, redundant entry, and accessible authentication.[1] Use semantic HTML, visible keyboard focus, sufficient contrast, and controls that are large enough for pointer and touch input. Material guidance reinforces using native controls and translating the visual design into a linear, text-based experience that maps cleanly to code.[7]

Forms should use a vertical structure, explicit labels, fieldsets and legends for related radio options, inline validation, and clear required or optional states. USWDS recommends these patterns and cautions against relying on disabled controls as the primary explanation of what users should do.[5] Error messages should state what went wrong and how to fix it. The same message should not exist only in a toast, console log, or color change.

Copy should use the assessor’s users’ language rather than internal engineering terms. Each page should have one clear H1, a short purpose statement, sentence-case labels, and no unnecessary help text. GOV.UK’s interface-writing guidance links clear language directly to reduced cognitive load and fewer mistakes.[3] Nielsen’s heuristics add the need for visible system status, recognition rather than recall, user control, error prevention, and recovery.[4]

## Recommended user journey

The lowest-friction journey is:

1. Sign in or create an account with clear password guidance.
2. See a dashboard with one primary action, recent assessments, completion state, and a short explanation of the four risk stages.
3. Create an assessment with only a title, system purpose, owner, and optional description.
4. Complete a short context step that determines which later questions are relevant.
5. Work through one question at a time or a small related group, with autosave, progress, a back action, and a visible “saved” state.
6. Review answers before submission, with a change link for each section.
7. Receive a report that explains score, maturity, evidence gaps, priority actions, affected AI RMF stage, and export options.

The click-complexity target should be one primary decision per screen, no more than one required navigation decision between questions, and no requirement to reopen completed sections merely to remember previous answers. A user should always know where they are, what remains, and whether leaving the page will lose work.

## Prioritized backlog

**P0 — completed in this pass.** Restore the CSS toolchain, replace the accidental dark default, add visible focus treatment, ensure the application router is mounted, and keep Docker startup detached and health-checkable. These changes remove the current “looks broken” and “blank interface” barriers.

**P1 — next implementation pass.** Add semantic labels and IDs, `aria-describedby` helper text, an accessible error summary, dialog semantics and focus return for the create-assessment modal, keyboard operation for assessment cards, and a real loading/error/empty state system. Add progress and saved-state feedback to the assessment page. Add a visible score legend and action priorities to the report.

**P2 — workflow redesign.** Introduce a question protocol and branching model. Group questions by Govern, Map, Measure, and Manage. Store draft answers incrementally. Add a review-and-submit screen. Replace generic console errors with user-facing recovery messages and retry actions.

**P3 — evidence and trust.** Let users attach or reference evidence, record who answered and when, show confidence and evidence completeness separately from risk score, and provide an audit trail for changes. Keep synthetic data as the default demonstration path.

## Sharing the running local interface

A `localhost` URL is reachable only from the computer running Docker. For another device on the same home or office network, find the Windows machine’s IPv4 address with `ipconfig`, ensure Windows Firewall permits inbound TCP 80, and open `http://<PC-IP>/login` from the other device. This should be limited to a trusted network and synthetic data.

For a temporary HTTPS URL, Cloudflare Quick Tunnels are the simplest option. After installing `cloudflared`, run `cloudflared tunnel --url http://localhost:80`. Cloudflare documents that the generated `trycloudflare.com` URL is temporary and stops working when the process stops; anyone with the URL can access the service, so use an email restriction such as `--allowed-mail your-reviewer@example.com` when possible.[8]

If the devices are already in one Tailscale network, use Tailscale Serve for tailnet-only access. Tailscale Funnel is the public-internet alternative and provides HTTPS, but it should be treated as an external exposure rather than a private preview.[9] ngrok is another option after installing the agent and configuring its token; its documented command is `ngrok http 80`.[10]

A shareable tunnel URL can be provided for a direct visual review of the running app. Do not expose production secrets, real personal data, or real assessment records through a temporary tunnel. Use the local development `.env`, synthetic accounts, and destroy the tunnel after review.

## Acceptance criteria for the next UX release

The next release should pass a keyboard-only walkthrough, a screen-reader-oriented semantic review, a 375-pixel mobile layout review, and a complete synthetic journey from registration through report export. It should show healthy Docker services without requiring an attached terminal, present a non-blank styled interface, preserve draft answers across a refresh, explain every validation error at the field that caused it, and make the report actionable without requiring the user to interpret a raw score.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"
[2]: https://www.gov.uk/service-manual/design/form-structure "GOV.UK: Structuring forms"
[3]: https://www.gov.uk/service-manual/design/writing-for-user-interfaces "GOV.UK: Writing for user interfaces"
[4]: https://www.nngroup.com/articles/ten-usability-heuristics/ "Nielsen Norman Group: 10 Usability Heuristics for User Interface Design"
[5]: https://designsystem.digital.gov/components/form/ "U.S. Web Design System: Form"
[6]: https://www.nist.gov/itl/ai-risk-management-framework "NIST AI Risk Management Framework"
[7]: https://m3.material.io/foundations/designing "Material Design 3: Designing accessible experiences"
[8]: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/ "Cloudflare Quick Tunnels"
[9]: https://tailscale.com/docs/reference/tailscale-cli/funnel "Tailscale Funnel"
[10]: https://ngrok.com/docs/start "ngrok: Get Started"
