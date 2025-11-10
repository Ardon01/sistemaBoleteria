# Test Suite Documentation

Este proyecto incluye un conjunto completo de pruebas unitarias e integración para el Sistema de Boletería de Eventos.

## Estructura de Pruebas

\`\`\`
__tests__/
├── setup.ts                          # Configuración global de pruebas
├── components/                       # Pruebas de componentes UI
│   └── ui/
│       ├── button.test.tsx
│       ├── card.test.tsx
│       └── input.test.tsx
├── hooks/                           # Pruebas de React hooks
│   ├── use-toast.test.ts
│   └── use-mobile.test.ts
├── lib/                             # Pruebas de utilidades
│   └── utils.test.ts
├── utils/                           # Pruebas de funciones auxiliares
│   ├── validation.test.ts
│   └── formatters.test.ts
├── models/                          # Pruebas de modelos de datos
│   ├── event.test.ts
│   └── ticket.test.ts
└── integration/                     # Pruebas de integración
    └── event-booking.test.tsx
\`\`\`

## Ejecutar Pruebas

### Ejecutar todas las pruebas
\`\`\`bash
npm test
\`\`\`

### Ejecutar pruebas en modo watch
\`\`\`bash
npm run test:watch
\`\`\`

### Generar reporte de cobertura
\`\`\`bash
npm run test:coverage
\`\`\`

## Cobertura de Pruebas

Las pruebas cubren:

### Componentes UI
- ✅ Button: Variantes, tamaños, estados disabled
- ✅ Card: Estructura completa con subcomponentes
- ✅ Input: Tipos, validación, eventos

### Hooks Personalizados
- ✅ useToast: Agregar, actualizar, eliminar notificaciones
- ✅ useMobile: Detección de viewport móvil

### Utilidades
- ✅ cn(): Fusión de clases CSS con Tailwind
- ✅ Validación: Email, contraseña, fecha, precio
- ✅ Formateo: Moneda, fecha, hora

### Modelos de Negocio
- ✅ Event Model: CRUD completo de eventos
- ✅ Ticket Model: Reserva, venta, validación QR

### Integración
- ✅ Flujo completo de compra de boletos

## Convenciones de Testing

### Estructura de Pruebas
\`\`\`typescript
describe('Component/Feature Name', () => {
  describe('Functionality Group', () => {
    it('should describe expected behavior', () => {
      // Arrange
      // Act
      // Assert
    })
  })
})
\`\`\`

### Naming Conventions
- Usa nombres descriptivos que expliquen el comportamiento esperado
- Inicia con "should" para casos positivos
- Usa "should not" para casos negativos

### Best Practices
1. Cada prueba debe ser independiente
2. Usa `beforeEach` para configuración común
3. Limpia después de cada prueba si es necesario
4. Mockea dependencias externas
5. Prueba casos de error además de casos exitosos

## Tipos de Pruebas

### Unit Tests
Prueban componentes y funciones de forma aislada.

### Integration Tests
Prueban la interacción entre múltiples componentes.

### Coverage Goals
- Líneas: > 80%
- Funciones: > 80%
- Branches: > 75%

## Debugging Pruebas

Para depurar una prueba específica:
\`\`\`bash
npm test -- --watch button.test
\`\`\`

Para ver output detallado:
\`\`\`bash
npm test -- --verbose
\`\`\`

## Agregar Nuevas Pruebas

1. Crea un archivo `*.test.ts` o `*.test.tsx`
2. Importa las funciones de testing necesarias
3. Sigue la estructura describe/it
4. Ejecuta las pruebas para verificar

## Tecnologías Utilizadas

- **Jest**: Framework de testing
- **React Testing Library**: Testing de componentes React
- **@testing-library/user-event**: Simulación de interacciones
- **@testing-library/jest-dom**: Matchers adicionales para DOM
