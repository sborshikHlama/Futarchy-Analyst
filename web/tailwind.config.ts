import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg:           '#151B2B',
        surface:      '#1E2638',
        'surface-2':  '#252E42',
        border:       'rgba(255,255,255,0.07)',
        'border-soft':'rgba(255,255,255,0.04)',
        fg:           '#F8FAFC',
        'fg-muted':   '#94A3B8',
        'fg-faint':   '#64748B',
        accent:       '#3DE0A5',
        'accent-dark':'#2BB887',
        'accent-soft':'rgba(61,224,165,0.12)',
        bull:         '#3DE0A5',
        'bull-soft':  'rgba(61,224,165,0.08)',
        bear:         '#F87171',
        'bear-soft':  'rgba(248,113,113,0.08)',
        warn:         '#F59E0B',
        'warn-soft':  'rgba(245,158,11,0.08)',
        neutral:      '#94A3B8',
      },
      fontFamily: {
        heading: ['Outfit', '-apple-system', 'system-ui', 'sans-serif'],
        sans:    ['Inter', '-apple-system', 'system-ui', 'sans-serif'],
        mono:    ['JetBrains Mono', 'ui-monospace', 'SF Mono', 'monospace'],
      },
      fontSize: {
        '10': ['10px', '14px'],
        '11': ['11px', '15px'],
        '12': ['12px', '16px'],
        '13': ['13px', '18px'],
        '14': ['14px', '20px'],
        '15': ['15px', '22px'],
        '24': ['24px', '30px'],
        '28': ['28px', '34px'],
        '36': ['36px', '42px'],
      },
      borderRadius: {
        'pill': '9999px',
        'card': '24px',
        'md':   '16px',
        'sm':   '12px',
      },
      maxWidth: {
        'memo':     '880px',
        'prose-65': '65ch',
      },
      borderWidth: { '3': '3px' },
      boxShadow: {
        'mint':     '0 8px 24px -4px rgba(61,224,165,0.25)',
        'mint-lg':  '0 0 40px rgba(61,224,165,0.12)',
        'card':     '0 0 0 1px rgba(255,255,255,0.06)',
      },
      animation: {
        'fade-in':    'fadeIn 0.25s ease-out',
        'pulse-live': 'pulse-live 2s ease-in-out infinite',
        'glow':       'glow-pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
