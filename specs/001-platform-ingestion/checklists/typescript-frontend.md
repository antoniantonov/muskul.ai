# TypeScript Frontend Quality Checklist

**Agent**: `@typescript` | **Scope**: `frontend/src/`, `frontend/tests/`

This checklist ensures all TypeScript/React frontend code meets production-grade quality standards before marking tasks complete.

---

## Code Quality

- [ ] **TypeScript Strict Mode**: `tsconfig.json` has `"strict": true` enabled
- [ ] **No `any` Types**: No use of `any` type (use `unknown` or proper types)
- [ ] **Type Definitions**: All props, state, hooks have explicit TypeScript types
- [ ] **Linting**: All code passes `npm run lint` (ESLint) with zero errors/warnings
- [ ] **Formatting**: All code passes `npm run format:check` (Prettier) with no changes needed
- [ ] **Import Order**: Imports organized (React → third-party → internal → styles)
- [ ] **Unused Imports**: No unused imports or variables
- [ ] **Console Logs**: No `console.log` statements in production code (use proper logging)

---

## Testing

- [ ] **Unit Tests**: All utility functions and custom hooks have unit tests (Vitest)
- [ ] **Component Tests**: All components have tests using React Testing Library
- [ ] **User-Centric Queries**: Tests use `getByRole`, `getByLabelText` (not `getByTestId` unless necessary)
- [ ] **Coverage - Overall**: ≥80% code coverage via `npm run coverage`
- [ ] **Coverage - Critical Flows**: ≥90% coverage for critical user flows (auth, data import, dashboard)
- [ ] **Test Naming**: Tests follow `it('should <expected behavior> when <scenario>')` convention
- [ ] **Test Isolation**: Each test is independent, no shared state between tests
- [ ] **Accessibility Tests**: Components tested with `axe-core` (via `jest-axe` or `vitest-axe`)
- [ ] **E2E Tests**: Critical user flows covered by Playwright tests in `tests/e2e/`

---

## Accessibility (WCAG 2.1 AA)

- [ ] **Semantic HTML**: Use proper HTML5 elements (`<button>`, `<nav>`, `<main>`, `<article>`, etc.)
- [ ] **ARIA Labels**: Interactive elements have `aria-label` or `aria-labelledby`
- [ ] **ARIA Descriptions**: Complex elements have `aria-describedby` where needed
- [ ] **Keyboard Navigation**: All interactive elements accessible via keyboard (Tab, Enter, Space, Arrow keys)
- [ ] **Focus Management**: Visible focus indicators, focus trap for modals, focus restoration
- [ ] **Color Contrast**: Text contrast ≥4.5:1 (normal text), ≥3:1 (large text) - verify with contrast checker
- [ ] **Form Labels**: All form inputs have associated `<label>` elements
- [ ] **Error Messages**: Form validation errors announced to screen readers (`aria-live`, `role="alert"`)
- [ ] **Alt Text**: All images have descriptive `alt` attributes (empty `alt=""` for decorative images)
- [ ] **axe-core Audit**: `npm run axe` passes with zero violations

---

## Performance

- [ ] **Lighthouse Score**: Score ≥90 for Performance, Accessibility, Best Practices, SEO
- [ ] **First Contentful Paint (FCP)**: <1.5s on 3G Fast network
- [ ] **Time to Interactive (TTI)**: <3s on 3G Fast network
- [ ] **Cumulative Layout Shift (CLS)**: <0.1 (no unexpected layout shifts)
- [ ] **Bundle Size**: Main bundle <200KB gzipped (use `npm run build` and check dist/)
- [ ] **Code Splitting**: Routes lazy-loaded with `React.lazy()` and `Suspense`
- [ ] **Memoization**: Expensive calculations use `useMemo`, callbacks use `useCallback`
- [ ] **Image Optimization**: Images use WebP format, lazy-loaded with `loading="lazy"`
- [ ] **Tree Shaking**: No unused dependencies in final bundle

---

## UX & Design

- [ ] **Loading States**: All async operations show loading indicators (spinners, skeletons)
- [ ] **Error Handling**: Errors displayed with clear messages and recovery actions
- [ ] **Empty States**: Lists/tables show helpful empty states ("No data yet", with call-to-action)
- [ ] **Responsive Design**: Components work on mobile (320px), tablet (768px), desktop (1024px+)
- [ ] **Touch-Friendly**: Tap targets ≥44px × 44px on mobile (buttons, links, interactive elements)
- [ ] **Tailwind CSS**: All styling uses Tailwind utility classes (no inline styles or CSS files unless necessary)
- [ ] **Design Tokens**: Colors, spacing, typography use Tailwind config variables
- [ ] **Dark Mode Support**: (If required) Components support dark mode via Tailwind `dark:` variants

---

## Data Fetching & State

- [ ] **React Query**: All API calls use React Query (`useQuery`, `useMutation`)
- [ ] **Cache Configuration**: React Query cache configured with appropriate `staleTime` and `cacheTime`
- [ ] **Optimistic Updates**: Mutations use optimistic updates where appropriate
- [ ] **Error Boundaries**: Components wrapped in error boundaries for graceful error handling
- [ ] **Zod Validation**: API responses validated with Zod schemas before use
- [ ] **Loading States**: React Query loading states handled (`isLoading`, `isFetching`)
- [ ] **Retry Logic**: Failed requests retry with exponential backoff (React Query `retry` config)

---

## Component Architecture

- [ ] **Functional Components**: All components are functional (no class components)
- [ ] **Single Responsibility**: Each component has one clear purpose
- [ ] **Reusable Components**: Shared components in `components/`, page-specific in `pages/`
- [ ] **Props Validation**: All props have TypeScript types (interfaces or types)
- [ ] **Custom Hooks**: Reusable logic extracted into custom hooks in `hooks/`
- [ ] **Component Composition**: Prefer composition over prop drilling (use Context API or React Query)
- [ ] **No Prop Drilling**: Avoid passing props through 3+ levels (use Context or state management)

---

## Security

- [ ] **XSS Prevention**: All user input sanitized before rendering (React auto-escapes, but verify)
- [ ] **No `dangerouslySetInnerHTML`**: Avoid unless absolutely necessary and input is sanitized
- [ ] **HTTPS API Calls**: All API requests use HTTPS (no hardcoded HTTP URLs)
- [ ] **Token Storage**: Auth tokens stored in `httpOnly` cookies or secure storage (not localStorage for sensitive tokens)
- [ ] **CSRF Protection**: API requests include CSRF tokens where required
- [ ] **Content Security Policy**: CSP headers configured in deployment (if applicable)

---

## Task Completion Validation

Before marking a TypeScript frontend task as `[X]` complete:

1. ✅ Run `npm run type-check` - no TypeScript errors
2. ✅ Run `npm run lint` - no ESLint errors/warnings
3. ✅ Run `npm run format:check` - Prettier formatting correct
4. ✅ Run `npm test` - all tests pass
5. ✅ Run `npm run coverage` - coverage thresholds met (≥80% overall, ≥90% critical flows)
6. ✅ Run `npm run build` - build succeeds, check bundle size
7. ✅ Run Lighthouse audit - score ≥90 for all categories
8. ✅ Run `axe-core` audit - zero accessibility violations
9. ✅ Verify all checklist items above are complete for the specific task

---

**Agent Reference**: `.github/agents/typescript.agent.md`  
**Last Updated**: 2025-11-23
