"use client"

import { describe, it, expect, jest } from "@jest/globals"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Input } from "@/components/ui/input"

describe("Input Component", () => {
  it("should render input field", () => {
    render(<Input placeholder="Enter text" />)
    const input = screen.getByPlaceholderText("Enter text")
    expect(input).toBeInTheDocument()
  })

  it("should handle user input", async () => {
    const user = userEvent.setup()
    render(<Input placeholder="Type here" />)
    const input = screen.getByPlaceholderText("Type here") as HTMLInputElement

    await user.type(input, "Hello World")
    expect(input.value).toBe("Hello World")
  })

  it("should be disabled when disabled prop is true", () => {
    render(<Input disabled placeholder="Disabled input" />)
    const input = screen.getByPlaceholderText("Disabled input")
    expect(input).toBeDisabled()
  })

  it("should handle different input types", () => {
    const { rerender } = render(<Input type="text" />)
    let input = screen.getByRole("textbox")
    expect(input).toHaveAttribute("type", "text")

    rerender(<Input type="email" />)
    input = screen.getByRole("textbox")
    expect(input).toHaveAttribute("type", "email")
  })

  it("should call onChange handler", async () => {
    const handleChange = jest.fn()
    const user = userEvent.setup()

    render(<Input onChange={handleChange} placeholder="Test" />)
    const input = screen.getByPlaceholderText("Test")

    await user.type(input, "a")
    expect(handleChange).toHaveBeenCalled()
  })
})
