import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import App from './App'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const data = url.includes('/graph')
      ? { nodes: [{ id: 'concepts/okf', label: 'OKF', type: 'Concept', tags: ['okf'] }, { id: 'sources/okf-spec', label: 'OKF specification', type: 'Source', tags: ['okf'] }], edges: [] }
      : [
        { id: 'concepts/okf', type: 'Concept', title: 'OKF', description: 'Open Knowledge Format', tags: ['okf'], resource: null, timestamp: null, body: '# Overview', links: [] },
        { id: 'sources/okf-spec', type: 'Source', title: 'OKF specification', title_ko: 'OKF 명세', description: 'Official source capture', description_ko: '공식 원문 보존본', tags: ['okf'], resource: null, timestamp: null, body: '# Source', body_ko: '# 출처\n\n공식 원문 보존본입니다.', links: [] },
      ]
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) })
  }))
})

test('renders the knowledge workspace with a document and graph view', async () => {
  render(<App />)

  expect(await screen.findByText('OKF')).toBeInTheDocument()
  expect(screen.getByText('지식 그래프')).toBeInTheDocument()
  expect(screen.getAllByText('Open Knowledge Format').length).toBeGreaterThan(0)
})

test('opens the manual OKF ingestion form', async () => {
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /문서 추가/i }))

  expect(await screen.findByLabelText('문서 제목')).toBeInTheDocument()
  expect(screen.getByLabelText('Markdown 본문')).toBeInTheDocument()
})

test('groups documents in the Korean sidebar and opens a readable document detail view', async () => {
  render(<App />)

  expect(await screen.findByText('문서 탐색')).toBeInTheDocument()
  expect(screen.getByText('개념', { selector: '.group-title span' })).toBeInTheDocument()
  expect(screen.getByText('출처', { selector: '.group-title span' })).toBeInTheDocument()
  const sourceButtons = screen.getAllByRole('button', { name: 'OKF specification' })
  fireEvent.click(sourceButtons[0])

  const detail = await screen.findByRole('dialog', { name: 'OKF specification 상세 문서' })
  expect(detail).toHaveTextContent('Official source capture')
  expect(detail).toHaveTextContent('Source')
  expect(detail).not.toHaveTextContent('# Source')
  fireEvent.click(screen.getByRole('button', { name: '한국어' }))
  expect(detail).toHaveTextContent('OKF 명세')
  expect(detail).toHaveTextContent('공식 원문 보존본입니다.')
})
