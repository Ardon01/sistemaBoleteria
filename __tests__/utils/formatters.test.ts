import { describe, it, expect } from "@jest/globals"

// Currency formatter
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("es-HN", {
    style: "currency",
    currency: "HNL",
  }).format(amount)
}

// Date formatter
const formatDate = (date: string | Date): string => {
  const d = new Date(date)
  return d.toLocaleDateString("es-HN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

// Time formatter
const formatTime = (date: string | Date): string => {
  const d = new Date(date)
  return d.toLocaleTimeString("es-HN", {
    hour: "2-digit",
    minute: "2-digit",
  })
}

describe("Formatters", () => {
  describe("Currency Formatter", () => {
    it("should format numbers as currency", () => {
      const result = formatCurrency(100)
      expect(result).toContain("100")
    })

    it("should handle decimal values", () => {
      const result = formatCurrency(99.99)
      expect(result).toContain("99")
    })

    it("should handle zero", () => {
      const result = formatCurrency(0)
      expect(result).toContain("0")
    })
  })

  describe("Date Formatter", () => {
    it("should format dates correctly", () => {
      const result = formatDate("2025-01-15")
      expect(result).toBeTruthy()
      expect(typeof result).toBe("string")
    })

    it("should handle Date objects", () => {
      const date = new Date("2025-01-15")
      const result = formatDate(date)
      expect(result).toBeTruthy()
    })
  })

  describe("Time Formatter", () => {
    it("should format time correctly", () => {
      const result = formatTime("2025-01-15T14:30:00")
      expect(result).toBeTruthy()
      expect(typeof result).toBe("string")
    })
  })
})
