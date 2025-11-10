import { describe, it, expect } from "@jest/globals"
import { cn } from "@/lib/utils"

describe("Utils", () => {
  describe("cn function", () => {
    it("should merge class names correctly", () => {
      const result = cn("class1", "class2")
      expect(result).toContain("class1")
      expect(result).toContain("class2")
    })

    it("should handle conditional classes", () => {
      const result = cn("base", false && "hidden", true && "visible")
      expect(result).toContain("base")
      expect(result).toContain("visible")
      expect(result).not.toContain("hidden")
    })

    it("should handle undefined and null values", () => {
      const result = cn("base", undefined, null, "valid")
      expect(result).toContain("base")
      expect(result).toContain("valid")
    })

    it("should merge Tailwind conflicting classes", () => {
      const result = cn("px-2", "px-4")
      // twMerge should keep only the last px class
      expect(result).toBe("px-4")
    })
  })
})
