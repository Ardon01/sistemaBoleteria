"use client"

import { describe, it, expect, beforeEach } from "@jest/globals"
import { renderHook, act } from "@testing-library/react"
import { useToast } from "@/hooks/use-toast"

describe("useToast Hook", () => {
  beforeEach(() => {
    // Reset toast state before each test
    const { result } = renderHook(() => useToast())
    act(() => {
      result.current.toasts.forEach((toast) => {
        result.current.dismiss(toast.id)
      })
    })
  })

  it("should add a toast", () => {
    const { result } = renderHook(() => useToast())

    act(() => {
      result.current.toast({
        title: "Test Toast",
        description: "This is a test",
      })
    })

    expect(result.current.toasts).toHaveLength(1)
    expect(result.current.toasts[0].title).toBe("Test Toast")
  })

  it("should dismiss a toast", () => {
    const { result } = renderHook(() => useToast())

    let toastId: string
    act(() => {
      const toast = result.current.toast({
        title: "Test Toast",
      })
      toastId = toast.id
    })

    expect(result.current.toasts).toHaveLength(1)

    act(() => {
      result.current.dismiss(toastId)
    })

    expect(result.current.toasts).toHaveLength(0)
  })

  it("should handle multiple toasts", () => {
    const { result } = renderHook(() => useToast())

    act(() => {
      result.current.toast({ title: "Toast 1" })
      result.current.toast({ title: "Toast 2" })
      result.current.toast({ title: "Toast 3" })
    })

    expect(result.current.toasts).toHaveLength(3)
  })

  it("should update existing toast", () => {
    const { result } = renderHook(() => useToast())

    let toastId: string
    act(() => {
      const toast = result.current.toast({
        title: "Original Title",
      })
      toastId = toast.id
    })

    act(() => {
      result.current.toast({
        id: toastId,
        title: "Updated Title",
      })
    })

    expect(result.current.toasts).toHaveLength(1)
    expect(result.current.toasts[0].title).toBe("Updated Title")
  })
})
