import { createFileRoute } from '@tanstack/react-router'
import { auth, ensureAuthSchema } from '#/lib/auth'

export const Route = createFileRoute('/api/auth/$')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        await ensureAuthSchema()
        return auth.handler(request)
      },
      POST: async ({ request }) => {
        await ensureAuthSchema()
        return auth.handler(request)
      },
    },
  },
})
