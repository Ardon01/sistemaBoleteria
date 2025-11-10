import { describe, it, expect } from "@jest/globals"

// Email validation function
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Password validation function
const isValidPassword = (password: string): boolean => {
  return password.length >= 8
}

// Date validation function
const isValidDate = (date: string): boolean => {
  const parsedDate = new Date(date)
  return !isNaN(parsedDate.getTime())
}

// Price validation function
const isValidPrice = (price: number): boolean => {
  return price > 0 && Number.isFinite(price)
}

describe("Validation Utils", () => {
  describe("Email Validation", () => {
    it("should validate correct email addresses", () => {
      expect(isValidEmail("test@example.com")).toBe(true)
      expect(isValidEmail("user.name@domain.co")).toBe(true)
      expect(isValidEmail("email+tag@test.org")).toBe(true)
    })

    it("should reject invalid email addresses", () => {
      expect(isValidEmail("invalid")).toBe(false)
      expect(isValidEmail("test@")).toBe(false)
      expect(isValidEmail("@example.com")).toBe(false)
      expect(isValidEmail("test @example.com")).toBe(false)
    })
  })

  describe("Password Validation", () => {
    it("should accept passwords with 8 or more characters", () => {
      expect(isValidPassword("12345678")).toBe(true)
      expect(isValidPassword("securePassword123")).toBe(true)
    })

    it("should reject passwords with less than 8 characters", () => {
      expect(isValidPassword("short")).toBe(false)
      expect(isValidPassword("1234567")).toBe(false)
    })
  })

  describe("Date Validation", () => {
    it("should validate correct date formats", () => {
      expect(isValidDate("2025-01-15")).toBe(true)
      expect(isValidDate("2025-12-31")).toBe(true)
    })

    it("should reject invalid dates", () => {
      expect(isValidDate("invalid-date")).toBe(false)
      expect(isValidDate("2025-13-01")).toBe(false)
    })
  })

  describe("Price Validation", () => {
    it("should validate positive prices", () => {
      expect(isValidPrice(10)).toBe(true)
      expect(isValidPrice(99.99)).toBe(true)
    })

    it("should reject invalid prices", () => {
      expect(isValidPrice(0)).toBe(false)
      expect(isValidPrice(-10)).toBe(false)
      expect(isValidPrice(Number.POSITIVE_INFINITY)).toBe(false)
    })
  })
})
