export const PLANS = {
  free: {
    name:     'Free',
    price:    0,
    memos:    3,
    features: ['3 memos/month', 'Public markets only', '48h delay'],
  },
  pro: {
    name:         'Pro',
    priceMonthly: 9,
    priceYearly:  79,
    memos:        Infinity,
    features: [
      'Unlimited memos',
      'Live Watch access',
      'All markets',
      'Real-time signals',
      'Full audit trail',
      'PnL tracking',
    ],
  },
}
