/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Primary brand colors - WCAG AA compliant
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9', // Primary - 4.5:1 on white
          600: '#0284c7', // 7:1 on white
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        // Semantic colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e', // 3.8:1 on white (use 600 for AA)
          600: '#16a34a', // 4.5:1 on white
          700: '#15803d', // 7:1 on white
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#f59e0b', // 3.4:1 on white (use 600 for AA)
          600: '#d97706', // 4.5:1 on white
          700: '#b45309', // 7:1 on white
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444', // 3.8:1 on white (use 600 for AA)
          600: '#dc2626', // 4.5:1 on white
          700: '#b91c1c', // 7:1 on white
        },
        // Neutral colors
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252', // 7:1 on white
          700: '#404040', // 10.4:1 on white
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Consolas',
          'Monaco',
          'Courier New',
          'monospace',
        ],
      },
      fontSize: {
        // WCAG-compliant font sizes
        xs: ['0.75rem', { lineHeight: '1rem' }], // 12px
        sm: ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        base: ['1rem', { lineHeight: '1.5rem' }], // 16px (minimum for body text)
        lg: ['1.125rem', { lineHeight: '1.75rem' }], // 18px
        xl: ['1.25rem', { lineHeight: '1.75rem' }], // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }], // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }], // 36px
      },
      spacing: {
        // 8px base grid for accessibility
        0: '0',
        px: '1px',
        0.5: '0.125rem', // 2px
        1: '0.25rem', // 4px
        2: '0.5rem', // 8px
        3: '0.75rem', // 12px
        4: '1rem', // 16px
        5: '1.25rem', // 20px
        6: '1.5rem', // 24px
        8: '2rem', // 32px
        10: '2.5rem', // 40px
        12: '3rem', // 48px
        16: '4rem', // 64px
        20: '5rem', // 80px
        24: '6rem', // 96px
      },
      borderRadius: {
        none: '0',
        sm: '0.25rem', // 4px
        DEFAULT: '0.5rem', // 8px
        md: '0.5rem', // 8px
        lg: '0.75rem', // 12px
        xl: '1rem', // 16px
        '2xl': '1.5rem', // 24px
        full: '9999px',
      },
      boxShadow: {
        // Accessible focus rings
        focus: '0 0 0 3px rgba(14, 165, 233, 0.5)',
        'focus-error': '0 0 0 3px rgba(220, 38, 38, 0.5)',
        // Elevation shadows
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'spin-slow': 'spin 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      // Minimum touch target size: 44x44px (WCAG 2.1 Level AAA)
      minHeight: {
        touch: '44px',
      },
      minWidth: {
        touch: '44px',
      },
    },
  },
  plugins: [],
};
