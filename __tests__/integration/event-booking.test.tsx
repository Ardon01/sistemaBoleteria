"use client"

import { describe, it, expect } from "@jest/globals"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import React from "react"

// Mock event booking flow
const MockEventBookingFlow = () => {
  const [step, setStep] = React.useState(1)
  const [selectedEvent, setSelectedEvent] = React.useState<string>("")
  const [quantity, setQuantity] = React.useState(1)

  return (
    <div>
      {step === 1 && (
        <div>
          <h2>Select Event</h2>
          <button
            onClick={() => {
              setSelectedEvent("Concert A")
              setStep(2)
            }}
          >
            Concert A
          </button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2>Select Quantity</h2>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            min={1}
            aria-label="quantity"
          />
          <button onClick={() => setStep(3)}>Continue to Payment</button>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2>Payment</h2>
          <p>Event: {selectedEvent}</p>
          <p>Quantity: {quantity}</p>
          <button>Confirm Payment</button>
        </div>
      )}
    </div>
  )
}

describe("Event Booking Integration", () => {
  it("should complete booking flow", async () => {
    const user = userEvent.setup()

    render(<MockEventBookingFlow />)

    // Step 1: Select event
    expect(screen.getByText("Select Event")).toBeInTheDocument()
    await user.click(screen.getByText("Concert A"))

    // Step 2: Select quantity
    expect(screen.getByText("Select Quantity")).toBeInTheDocument()
    const quantityInput = screen.getByLabelText("quantity")
    await user.clear(quantityInput)
    await user.type(quantityInput, "3")
    await user.click(screen.getByText("Continue to Payment"))

    // Step 3: Payment
    expect(screen.getByText("Payment")).toBeInTheDocument()
    expect(screen.getByText("Event: Concert A")).toBeInTheDocument()
    expect(screen.getByText("Quantity: 3")).toBeInTheDocument()
  })
})
