// Maps completion percentage to a karate belt rank — Dojo Hub's signature
// way of showing progress, instead of a generic green progress bar.
export const BELT_RANKS = [
  { max: 15, label: 'White Belt', color: '#F5F3EE', text: '#1a1a1a', border: '#D8D2C4' },
  { max: 30, label: 'Yellow Belt', color: '#F2C94C', text: '#1a1a1a', border: '#D9AE2E' },
  { max: 45, label: 'Orange Belt', color: '#F2994A', text: '#1a1a1a', border: '#D97B2A' },
  { max: 60, label: 'Green Belt', color: '#27AE60', text: '#ffffff', border: '#1F8A4D' },
  { max: 75, label: 'Blue Belt', color: '#2D9CDB', text: '#ffffff', border: '#2380B8' },
  { max: 90, label: 'Brown Belt', color: '#7B4B2A', text: '#ffffff', border: '#5E3A20' },
  { max: 100, label: 'Black Belt', color: '#1A1A1A', text: '#ffffff', border: '#C8102E' },
]

export function getBeltRank(percent) {
  if (percent >= 100) return BELT_RANKS[BELT_RANKS.length - 1]
  return BELT_RANKS.find((rank) => percent <= rank.max) ?? BELT_RANKS[0]
}
