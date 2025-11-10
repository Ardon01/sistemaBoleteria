"use client"

import { describe, it, expect, beforeEach, afterEach, jest } from "@jest/globals"
import { renderHook } from "@testing-library/react"
import { useMobile } from "@/hooks/use-mobile"

describe("useMobile Hook", () => {
  const originalMatchMedia = window.matchMedia

  beforeEach(() => {
    // Mock window.matchMedia
    window.matchMedia = jest.fn() as any
  })

  afterEach(() => {
    window.matchMedia = originalMatchMedia
  })

  it("should return true for mobile viewport", () => {
    ;(window.matchMedia as jest.MockedFunction<typeof window.matchMedia>).mockImplementation((query) => ({
      matches: query === "(max-width: 768px)",
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }))

    const { result } = renderHook(() => useMobile())
    expect(result.current).toBe(true)
  })

  it("should return false for desktop viewport", () => {
    ;(window.matchMedia as jest.MockedFunction<typeof window.matchMedia>).mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }))

    const { result } = renderHook(() => useMobile())
    expect(result.current).toBe(false)
  })
})
