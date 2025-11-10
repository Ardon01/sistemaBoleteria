import { describe, it, expect, beforeEach } from "@jest/globals"

interface Ticket {
  id: number
  id_evento: number
  id_categoria: number
  precio: number
  estado: "disponible" | "reservado" | "vendido"
  codigo_qr?: string
}

class TicketModel {
  private tickets: Ticket[] = []
  private nextId = 1

  create(ticketData: Omit<Ticket, "id">): Ticket {
    const newTicket: Ticket = {
      id: this.nextId++,
      ...ticketData,
    }
    this.tickets.push(newTicket)
    return newTicket
  }

  findAvailableByEvent(eventId: number): Ticket[] {
    return this.tickets.filter((ticket) => ticket.id_evento === eventId && ticket.estado === "disponible")
  }

  reserve(ticketId: number): boolean {
    const ticket = this.tickets.find((t) => t.id === ticketId)
    if (!ticket || ticket.estado !== "disponible") return false

    ticket.estado = "reservado"
    return true
  }

  sell(ticketId: number, qrCode: string): boolean {
    const ticket = this.tickets.find((t) => t.id === ticketId)
    if (!ticket || ticket.estado === "vendido") return false

    ticket.estado = "vendido"
    ticket.codigo_qr = qrCode
    return true
  }

  validateQR(qrCode: string): Ticket | null {
    const ticket = this.tickets.find((t) => t.codigo_qr === qrCode && t.estado === "vendido")
    return ticket || null
  }
}

describe("Ticket Model", () => {
  let ticketModel: TicketModel

  beforeEach(() => {
    ticketModel = new TicketModel()
  })

  describe("create", () => {
    it("should create a new ticket", () => {
      const ticket = ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "disponible",
      })

      expect(ticket.id).toBe(1)
      expect(ticket.estado).toBe("disponible")
    })
  })

  describe("findAvailableByEvent", () => {
    it("should return only available tickets for an event", () => {
      ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "disponible",
      })

      ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "vendido",
      })

      ticketModel.create({
        id_evento: 2,
        id_categoria: 1,
        precio: 300,
        estado: "disponible",
      })

      const available = ticketModel.findAvailableByEvent(1)
      expect(available).toHaveLength(1)
      expect(available[0].estado).toBe("disponible")
    })
  })

  describe("reserve", () => {
    it("should reserve an available ticket", () => {
      const ticket = ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "disponible",
      })

      const reserved = ticketModel.reserve(ticket.id)
      expect(reserved).toBe(true)

      const available = ticketModel.findAvailableByEvent(1)
      expect(available).toHaveLength(0)
    })

    it("should not reserve a non-available ticket", () => {
      const ticket = ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "vendido",
      })

      const reserved = ticketModel.reserve(ticket.id)
      expect(reserved).toBe(false)
    })
  })

  describe("sell", () => {
    it("should sell a ticket and assign QR code", () => {
      const ticket = ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "disponible",
      })

      const sold = ticketModel.sell(ticket.id, "QR123456")
      expect(sold).toBe(true)

      const foundTicket = ticketModel.validateQR("QR123456")
      expect(foundTicket).toBeDefined()
      expect(foundTicket?.id).toBe(ticket.id)
    })

    it("should not sell an already sold ticket", () => {
      const ticket = ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "vendido",
        codigo_qr: "EXISTING",
      })

      const sold = ticketModel.sell(ticket.id, "QR123456")
      expect(sold).toBe(false)
    })
  })

  describe("validateQR", () => {
    it("should validate a valid QR code", () => {
      const ticket = ticketModel.create({
        id_evento: 1,
        id_categoria: 1,
        precio: 500,
        estado: "vendido",
        codigo_qr: "VALID_QR",
      })

      const validated = ticketModel.validateQR("VALID_QR")
      expect(validated).toBeDefined()
      expect(validated?.id).toBe(ticket.id)
    })

    it("should return null for invalid QR code", () => {
      const validated = ticketModel.validateQR("INVALID_QR")
      expect(validated).toBeNull()
    })
  })
})
