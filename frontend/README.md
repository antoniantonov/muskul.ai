# Muskul.ai Frontend

React 18 + TypeScript 5 frontend application for the Muskul.ai fitness analytics platform.

## Tech Stack

- **Framework**: React 18.3+
- **Language**: TypeScript 5.5+ (strict mode)
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Routing**: React Router 6
- **Data Fetching**: TanStack Query (React Query)
- **Validation**: Zod
- **Charts**: Plotly.js (react-plotly.js)
- **Testing**: Vitest, React Testing Library, Playwright
- **Accessibility**: axe-core, WCAG 2.1 AA compliant

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.development

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking
- `npm run test` - Run unit tests with Vitest
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Generate test coverage report
- `npm run test:e2e` - Run E2E tests with Playwright
- `npm run test:e2e:ui` - Run E2E tests with Playwright UI
- `npm run test:a11y` - Run accessibility tests

## Project Structure

```
src/
├── components/       # Reusable UI components
├── pages/           # Page-level components
├── services/        # API clients and service layer
├── hooks/           # Custom React hooks
├── store/           # React Query setup and state management
├── types/           # TypeScript type definitions
├── styles/          # Global styles and Tailwind config
├── utils/           # Utility functions
├── test/            # Test setup and E2E tests
├── App.tsx          # Main app component with routing
└── main.tsx         # Application entry point
```

## Code Quality Standards

### TypeScript

- **Strict Mode**: Enabled (`"strict": true`)
- **No `any` types**: Use proper typing or `unknown`
- **Explicit return types**: Required for all functions
- **Path aliases**: Use `@/` for imports (e.g., `@/components/Button`)

### Accessibility (WCAG 2.1 AA)

- ✅ Color contrast ratio ≥ 4.5:1 for normal text
- ✅ Semantic HTML elements
- ✅ ARIA labels where needed
- ✅ Keyboard navigation support
- ✅ Focus indicators visible
- ✅ Minimum touch target size: 44x44px

### Performance Targets

- **Lighthouse Score**: ≥90
- **First Contentful Paint (FCP)**: <1.5s
- **Time to Interactive (TTI)**: <3s
- **Cumulative Layout Shift (CLS)**: <0.1
- **Bundle Size**: <200KB gzipped
- **Code Splitting**: React.lazy() for route-based splitting

### Component Guidelines

1. **Function components only** (no class components)
2. **TypeScript interfaces** for all props
3. **Explicit return types** for component functions
4. **Import order**: React → third-party → internal
5. **Tailwind CSS** for all styling (no inline styles)
6. **Accessibility first**: semantic HTML, ARIA labels, keyboard nav

### Example Component

```tsx
import React from 'react';
import { cn } from '@/utils/format';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  disabled?: boolean;
  ariaLabel?: string;
}

export function Button({
  children,
  variant = 'primary',
  onClick,
  disabled = false,
  ariaLabel,
}: ButtonProps): React.ReactElement {
  return (
    <button
      className={cn(
        'btn',
        variant === 'primary' ? 'btn-primary' : 'btn-secondary'
      )}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      type="button"
    >
      {children}
    </button>
  );
}
```

## Environment Variables

Create a `.env.development` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Testing

### Unit Tests

```bash
npm run test
```

### E2E Tests

```bash
npm run test:e2e
```

### Accessibility Tests

```bash
npm run test:a11y
```

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

Please ensure all code passes:
- TypeScript type checking (`npm run type-check`)
- ESLint (`npm run lint`)
- Prettier formatting (`npm run format:check`)
- All tests (`npm run test && npm run test:e2e`)
- Accessibility tests (`npm run test:a11y`)

## License

Proprietary - Muskul.ai
