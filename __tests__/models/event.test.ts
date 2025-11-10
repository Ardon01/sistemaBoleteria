import { describe, it, expect, beforeEach } from "@jest/globals"

interface Event {
  id: number
  nombre: string
  descripcion: string
  fecha_inicio: Date
  fecha_fin: Date
  lugar: string
  estado: "activo" | "cancelado" | "finalizado"
  precio_base: number
}

class EventModel {
  private events: Event[] = []
  private nextId = 1

  create(eventData: Omit<Event, "id">): Event {
    const newEvent: Event = {
      id: this.nextId++,
      ...eventData,
    }
    this.events.push(newEvent)
    return newEvent
  }

  findById(id: number): Event | undefined {
    return this.events.find((event) => event.id === id)
  }

  findByStatus(estado: Event["estado"]): Event[] {
    return this.events.filter((event) => event.estado === estado)
  }

  update(id: number, updates: Partial<Event>): Event | null {
    const index = this.events.findIndex((event) => event.id === id)
    if (index === -1) return null

    this.events[index] = { ...this.events[index], ...updates }
    return this.events[index]
  }

  delete(id: number): boolean {
    const index = this.events.findIndex((event) => event.id === id)
    if (index === -1) return false

    this.events.splice(index, 1)
    return true
  }

  getAll(): Event[] {
    return [...this.events]
  }
}

describe("Event Model", () => {
  let eventModel: EventModel

  beforeEach(() => {
    eventModel = new EventModel()
  })

  describe("create", () => {
    it("should create a new event", () => {
      const eventData = {
        nombre: "Concierto de Rock",
        descripcion: "Un evento musical increíble",
        fecha_inicio: new Date("2025-06-01"),
        fecha_fin: new Date("2025-06-01"),
        lugar: "Estadio Nacional",
        estado: "activo" as const,
        precio_base: 500,
      }

      const event = eventModel.create(eventData)

      expect(event.id).toBe(1)
      expect(event.nombre).toBe("Concierto de Rock")
      expect(event.estado).toBe("activo")
    })

    it("should auto-increment event IDs", () => {
      const eventData = {
        nombre: "Event 1",
        descripcion: "Description",
        fecha_inicio: new Date(),
        fecha_fin: new Date(),
        lugar: "Venue",
        estado: "activo" as const,
        precio_base: 100,
      }

      const event1 = eventModel.create(eventData)
      const event2 = eventModel.create(eventData)

      expect(event1.id).toBe(1)
      expect(event2.id).toBe(2)
    })
  })

  describe("findById", () => {
    it("should find an event by ID", () => {
      const eventData = {
        nombre: "Test Event",
        descripcion: "Description",
        fecha_inicio: new Date(),
        fecha_fin: new Date(),
        lugar: "Venue",
        estado: "activo" as const,
        precio_base: 100,
      }

      const created = eventModel.create(eventData)
      const found = eventModel.findById(created.id)

      expect(found).toBeDefined()
      expect(found?.id).toBe(created.id)
    })

    it("should return undefined for non-existent ID", () => {
      const found = eventModel.findById(999)
      expect(found).toBeUndefined()
    })
  })

  describe("findByStatus", () => {
    it("should filter events by status", () => {
      eventModel.create({
        nombre: "Active Event",
        descripcion: "Description",
        fecha_inicio: new Date(),
        fecha_fin: new Date(),
        lugar: "Venue",
        estado: "activo",
        precio_base: 100,
      })

      eventModel.create({
        nombre: "Cancelled Event",
        descripcion: "Description",
        fecha_inicio: new Date(),
        fecha_fin: new Date(),
        lugar: "Venue",
        estado: "cancelado",
        precio_base: 100,
      })

      const activeEvents = eventModel.findByStatus("activo")
      const cancelledEvents = eventModel.findByStatus("cancelado")

      expect(activeEvents).toHaveLength(1)
      expect(cancelledEvents).toHaveLength(1)
      expect(activeEvents[0].estado).toBe("activo")
    })
  })

  describe("update", () => {
    it("should update an existing event", () => {
      const event = eventModel.create({
        nombre: "Original Name",
        descripcion: "Description",
        fecha_inicio: new Date(),
        fecha_fin: new Date(),
        lugar: "Venue",
        estado: "activo",
        precio_base: 100,
      })

      const updated = eventModel.update(event.id, {
        nombre: "Updated Name",
        precio_base: 200,
      })

      expect(updated).toBeDefined()
      expect(updated?.nombre).toBe("Updated Name")
      expect(updated?.precio_base).toBe(200)
    })

    it("should return null for non-existent event", () => {
      const result = eventModel.update(999, { nombre: "Test" })
      expect(result).toBeNull()
    })
  })

  describe("delete", () => {
    it("should delete an event", () => {
      const event = eventModel.create({
        nombre: "Event to Delete",
        descripcion: "Description",
        fecha_inicio: new Date(),
        fecha_fin: new Date(),
        lugar: "Venue",
        estado: "activo",
        precio_base: 100,
      })

      const deleted = eventModel.delete(event.id)
      expect(deleted).toBe(true)

      const found = eventModel.findById(event.id)
      expect(found).toBeUndefined()
    })

    it("should return false for non-existent event", () => {
      const result = eventModel.delete(999)
      expect(result).toBe(false)
    })
  })
})
