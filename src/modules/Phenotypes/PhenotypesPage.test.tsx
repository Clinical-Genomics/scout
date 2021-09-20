import React from 'react'
import { Provider } from 'react-redux'
import { store } from '../../domain/store'
import { render, fireEvent, screen } from '@testing-library/react'
import { PhenotypesPage } from './PhenotypesPage'
import { windowMatchMedia } from '../../testHelpers'

describe('PhenotypesPage', () => {
  window.matchMedia = windowMatchMedia() as any
  test('PhenotypesPage render correctly', () => {
    const { getByTestId } = render(
      <Provider store={store}>
        <PhenotypesPage />
      </Provider>
    )
    const container = getByTestId('phenotypes')
    expect(container?.firstElementChild).toHaveAttribute('data-testid', 'test-phenotypes')
  })

  test('Download-btn render', () => {
    window.matchMedia = windowMatchMedia() as any
    render(
      <Provider store={store}>
        <PhenotypesPage />
      </Provider>
    )
    const download_btn = screen.getByRole('button', {
      name: /Download/i,
    })
    expect(download_btn).toBeInTheDocument()
  })

  test('CopyToClipboard-btn render', () => {
    window.matchMedia = windowMatchMedia() as any
    render(
      <Provider store={store}>
        <PhenotypesPage />
      </Provider>
    )
    const clipboard_btn = screen.getByRole('button', {
      name: /Copy to clipboard/i,
    })
    expect(clipboard_btn).toBeInTheDocument()
  })

  test('Add input', () => {
    window.matchMedia = windowMatchMedia() as any
    render(
      <Provider store={store}>
        <PhenotypesPage />
      </Provider>
    )
    const inputElement = screen.getByPlaceholderText('Search penotypes ...')
    expect(inputElement).toBeInTheDocument()
  })

  test('Should be able to type in input', () => {
    window.matchMedia = windowMatchMedia() as any
    render(
      <Provider store={store}>
        <PhenotypesPage />
      </Provider>
    )
    const inputElement = screen.getByPlaceholderText('Search penotypes ...') as HTMLInputElement
    fireEvent.change(inputElement, { target: { value: 'HP:0000002' } })
    expect(inputElement.value).toBe('HP:0000002')
  })

  test('Search for phenotypes', () => {
    window.matchMedia = windowMatchMedia() as any
    render(
      <Provider store={store}>
        <PhenotypesPage />
      </Provider>
    )
    const inputElement = screen.getByPlaceholderText('Search penotypes ...') as HTMLInputElement
    const buttonElement = screen.getByRole('button', {
      name: /Search/i,
    })
    fireEvent.change(inputElement, { target: { value: 'HP:0000002' } })
    expect(inputElement.value).toBe('HP:0000002')
    fireEvent.click(buttonElement)
    screen.findByText('Abnormality of body height')
  })
})
