'use client'

import Image from 'next/image'
import { useEffect, useRef, useState } from 'react'

// Mascot body color (mint blob)
const EYELID = '#3DD4A0'

// Eye positions at 32×32 rendered size.
// Tweak left/top/width/height if they feel off for the actual image.
const EYES = [
  { left: 8,  top: 13, width: 6, height: 7 }, // left eye
  { left: 18, top: 13, width: 6, height: 7 }, // right eye
]

async function sleep(ms: number) {
  return new Promise(r => setTimeout(r, ms))
}

export default function GlitchLogo() {
  const [closed, setClosed] = useState(false)
  const alive = useRef(true)

  useEffect(() => {
    alive.current = true

    async function loop() {
      while (alive.current) {
        // Wait between blinks
        await sleep(3000 + Math.random() * 5000)
        if (!alive.current) break

        // Blink once
        setClosed(true)
        await sleep(130)
        setClosed(false)

        // Occasionally double-blink
        if (Math.random() < 0.35) {
          await sleep(110)
          setClosed(true)
          await sleep(110)
          setClosed(false)
        }
      }
    }

    loop()
    return () => { alive.current = false }
  }, [])

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
      {/* Logo wrapper — eyelids positioned relative to the image */}
      <span style={{ position: 'relative', display: 'inline-flex', flexShrink: 0, width: 32, height: 32 }}>
        <Image
          src="/Mochifi_logo.png"
          alt="Mochifi"
          width={32}
          height={32}
          style={{ borderRadius: 8, objectFit: 'contain' }}
          priority
        />

        {EYES.map((eye, i) => (
          <span
            key={i}
            style={{
              position: 'absolute',
              left:   eye.left,
              top:    eye.top,
              width:  eye.width,
              height: eye.height,
              background: EYELID,
              borderRadius: '3px 3px 0 0',
              transformOrigin: 'top center',
              transform: closed ? 'scaleY(1)' : 'scaleY(0)',
              transition: closed
                ? 'transform 0.07s ease-in'
                : 'transform 0.09s ease-out',
            }}
          />
        ))}
      </span>

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
