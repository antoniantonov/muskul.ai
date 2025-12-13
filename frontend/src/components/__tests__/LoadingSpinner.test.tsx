import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '@/components/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders loading spinner with accessible label', () => {
    render(<LoadingSpinner />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
    
    const srText = screen.getByText('Loading...');
    expect(srText).toBeInTheDocument();
    expect(srText).toHaveClass('sr-only');
  });

  it('has proper ARIA attributes', () => {
    render(<LoadingSpinner />);
    
    const spinnerDiv = screen.getByLabelText('Loading');
    expect(spinnerDiv).toBeInTheDocument();
  });
});
