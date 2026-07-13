import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import App from './App'

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const data = url.includes('/graph')
      ? { nodes: [{ id: 'concepts/okf', label: 'OKF', type: 'Concept', tags: ['okf'] }, { id: 'sources/okf-spec', label: 'OKF specification', type: 'Source', tags: ['okf'] }], edges: [] }
      : [
        { id: 'concepts/okf', type: 'Concept', title: 'OKF', description: 'Open Knowledge Format', tags: ['okf'], resource: null, timestamp: null, body: '# Overview', links: [] },
        { id: 'sources/okf-spec', type: 'Source', title: 'OKF specification', title_ko: 'OKF 명세', description: 'Official source capture', description_ko: '공식 원문 보존본', tags: ['okf'], resource: null, timestamp: null, body: '# Source\n\nSee [official source](https://example.com), [OKF concept](/concepts/okf.md), and **preserved evidence**.\n\n1. First verification step\n2. Second verification step', body_ko: '# 출처\n\n공식 원문 보존본입니다.', links: [] },
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



test('labels graph navigation when the backend is Neo4j-backed', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const data = url.includes('/graph')
      ? { source: 'neo4j', nodes: [{ id: 'concepts/okf', label: 'OKF', type: 'Concept', tags: ['okf'] }], edges: [] }
      : [{ id: 'concepts/okf', type: 'Concept', title: 'OKF', description: 'Open Knowledge Format', tags: ['okf'], body: '# Overview', links: [] }]
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) })
  }))

  render(<App />)

  expect(await screen.findByText('Neo4j 관계 그래프')).toBeInTheDocument()
})
test('persists an explicit light and dark color mode choice', async () => {
  render(<App />)
  const toggle = await screen.findByRole('button', { name: /라이트 모드로 전환/i })
  fireEvent.click(toggle)
  expect(document.documentElement.dataset.theme).toBe('light')
  expect(screen.getByRole('button', { name: /다크 모드로 전환/i })).toBeInTheDocument()
})

test('opens the manual OKF ingestion form', async () => {
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /문서 추가/i }))

  expect(await screen.findByLabelText('문서 제목')).toBeInTheDocument()
  expect(screen.getByLabelText('Markdown 본문')).toBeInTheDocument()
})

test('opens and closes the compact mobile document navigation', async () => {
  render(<App />)
  const toggle = await screen.findByRole('button', { name: '문서 목록 열기' })
  expect(toggle).toHaveAttribute('aria-expanded', 'false')
  fireEvent.click(toggle)
  expect(screen.getByRole('button', { name: '문서 목록 닫기' })).toHaveAttribute('aria-expanded', 'true')
})

test('groups documents in the Korean sidebar and opens a readable document detail view', async () => {
  render(<App />)

  expect(await screen.findByText('문서 탐색')).toBeInTheDocument()
  expect(screen.getByText('지식 시스템', { selector: '.domain-title span' })).toBeInTheDocument()
  expect(screen.getByText('Knowledge architecture', { selector: '.topic-title' })).toBeInTheDocument()
  expect(screen.getByText('Specifications · evidence', { selector: '.topic-title' })).toBeInTheDocument()
  const sourceButtons = screen.getAllByTitle('OKF specification')
  fireEvent.click(sourceButtons[0])

  const detail = await screen.findByRole('dialog', { name: 'OKF specification 상세 문서' })
  expect(detail).toHaveTextContent('Official source capture')
  expect(detail).toHaveTextContent('Source')
  expect(detail).not.toHaveTextContent('# Source')
  expect(screen.getByRole('link', { name: 'official source' })).toHaveAttribute('href', 'https://example.com')
  expect(detail).toHaveTextContent('preserved evidence')
  expect(detail).toHaveTextContent('First verification step')
  expect(detail).toHaveTextContent('Second verification step')
  fireEvent.click(screen.getByRole('button', { name: '한국어' }))
  expect(detail).toHaveTextContent('OKF 명세')
  expect(detail).toHaveTextContent('공식 원문 보존본입니다.')
})

test('opens a linked local document inside the detail reader', async () => {
  render(<App />)
  fireEvent.click((await screen.findAllByTitle('OKF specification'))[0])
  fireEvent.click(await screen.findByRole('link', { name: 'OKF concept' }))

  const detail = await screen.findByRole('dialog', { name: 'OKF 상세 문서' })
  expect(detail).toHaveTextContent('Overview')
})

test('organizes the sidebar and graph by knowledge domain rather than document type', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    const data = url.includes('/graph')
      ? { nodes: [
        { id: 'concepts/system-design-learning-map', label: 'System design learning map', type: 'Concept', tags: ['system-design'] },
        { id: 'concepts/spring-kafka-listener-containers', label: 'Spring Kafka Listener Containers', type: 'Concept', tags: ['spring', 'kafka'] },
        { id: 'sources/spring-kafka', label: 'Spring Kafka source', type: 'Source', tags: ['spring', 'kafka'] },
      ], edges: [{ source: 'concepts/spring-kafka-listener-containers', target: 'sources/spring-kafka' }] }
      : [
        { id: 'concepts/system-design-learning-map', type: 'Concept', title: 'System design learning map', description: '', tags: ['system-design'], body: '# Map', links: [] },
        { id: 'concepts/spring-kafka-listener-containers', type: 'Concept', title: 'Spring Kafka Listener Containers', description: '', tags: ['spring', 'kafka'], body: '# Kafka', links: [] },
        { id: 'sources/spring-kafka', type: 'Source', title: 'Spring Kafka source', description: '', tags: ['spring', 'kafka'], body: '# Source', links: [] },
      ]
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) })
  }))

  render(<App />)
  expect(await screen.findByText('시스템 디자인', { selector: '.domain-title span' })).toBeInTheDocument()
  expect(screen.getByText('Spring', { selector: '.domain-title span' })).toBeInTheDocument()
  expect(screen.getByText('Kafka · messaging', { selector: '.topic-title' })).toBeInTheDocument()
  expect(screen.getByRole('img', { name: '지식 도메인 관계 그래프' })).toBeInTheDocument()
  expect(screen.getByText('SYSTEMS', { selector: '.graph-lane-label' })).toBeInTheDocument()
  expect(screen.getByText('SPRING', { selector: '.graph-lane-label' })).toBeInTheDocument()
})
