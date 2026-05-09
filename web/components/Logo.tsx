import Image from 'next/image'

/** Nav: маленький логотип + wordmark */
export function NavLogo() {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      <Image
        src="/logo.png"
        alt="Mochifi"
        width={28}
        height={28}
        style={{ borderRadius: 8, objectFit: 'cover', objectPosition: 'center' }}
        priority
      />
      <span
        style={{
          fontFamily: 'Outfit, sans-serif',
          fontWeight: 700,
          fontSize: 16,
          letterSpacing: '-0.02em',
          color: 'var(--fg)',
          lineHeight: 1,
        }}
      >
        Mochifi
      </span>
    </span>
  )
}

/** v1.0 badge рядом с логотипом */
export function LogoBadge() {
  return (
    <span
      style={{
        fontFamily: 'JetBrains Mono, monospace',
        fontWeight: 500,
        fontSize: 10,
        letterSpacing: '0.04em',
        background: 'rgba(61,224,165,0.12)',
        color: '#3DE0A5',
        border: '1px solid rgba(61,224,165,0.2)',
        borderRadius: 99,
        padding: '1px 8px',
        lineHeight: 1.6,
      }}
    >
      v1.0
    </span>
  )
}

/** Hero: большой логотип над заголовком */
export function HeroLogo() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 0 }}>
      <Image
        src="/logo.png"
        alt="Mochifi"
        width={72}
        height={72}
        style={{ borderRadius: 20, objectFit: 'cover', objectPosition: 'center' }}
        priority
      />
    </div>
  )
}

export default NavLogo
