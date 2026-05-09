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
        bg:         '#0B0D10',
        surface:    '#14171C',
        'surface-2':'#1B1F26',
        border:     '#262B33',
        'border-soft':'#1E232A',
        fg:         '#E6E8EB',
        'fg-muted': '#9AA1AB',
        'fg-faint': '#5E6772',
        accent:     '#5B5BD6',
        'accent-soft':'rgba(91,91,214,0.10)',
        bull:       '#2EBD85',
        'bull-soft':'rgba(46,189,133,0.08)',
        bear:       '#E5484D',
        'bear-soft':'rgba(229,72,77,0.08)',
        neutral:    '#9AA1AB',
        warn:       '#F5A524',
        'warn-soft':'rgba(245,165,36,0.08)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SF Mono', 'monospace'],
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
      },
      spacing: {
        '18': '72px',
      },
      maxWidth: {
        'memo': '880px',
        'prose-65': '65ch',
      },
      borderWidth: {
        '3': '3px',
      },
      animation: {
        'pulse-dot': 'pulse 2s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
      },
    },
  },
  plugins: [],
}

export default config
