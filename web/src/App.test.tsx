import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import App from './App'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const data = url.includes('/graph')
      ? { nodes: [{ id: 'concepts/okf', label: 'OKF', type: 'Concept', tags: ['okf'] }], edges: [] }
      : [{ id: 'concepts/okf', type: 'Concept', title: 'OKF', description: 'Open Knowledge Format', tags: ['okf'], resource: null, timestamp: null, body: '# Overview', links: [] }]
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) })
  }))
})

test('renders the knowledge workspace with a document and graph view', async () => {
  render(<App />)

  expect(await screen.findByText('OKF')).toBeInTheDocument()
  expect(screen.getByText('Knowledge Graph')).toBeInTheDocument()
  expect(screen.getAllByText('Open Knowledge Format').length).toBeGreaterThan(0)
})

test('opens the manual OKF ingestion form', async () => {
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /ingest document/i }))

  expect(await screen.findByLabelText('Document title')).toBeInTheDocument()
  expect(screen.getByLabelText('Markdown body')).toBeInTheDocument()
})
