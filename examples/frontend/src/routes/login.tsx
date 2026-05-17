import { Link, createFileRoute, useRouter } from '@tanstack/react-router'
import { useState, type FormEvent } from 'react'
import { authClient } from '#/lib/auth-client'

export const Route = createFileRoute('/login')({
  component: Login,
})

function Login() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    const { error: authError } = await authClient.signIn.email({
      email,
      password,
    })

    setIsSubmitting(false)

    if (authError) {
      setError(authError.message || 'Unable to sign in.')
      return
    }

    await router.navigate({ to: '/' })
  }

  return (
    <main className="min-h-screen bg-neutral-50 px-6 py-12 text-neutral-950">
      <section className="mx-auto flex w-full max-w-sm flex-col gap-6">
        <div>
          <h1 className="text-2xl font-semibold">Log in</h1>
          <p className="mt-2 text-sm text-neutral-600">
            Use the account stored in the local Better Auth SQLite database.
          </p>
        </div>

        <form
          className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm"
          onSubmit={handleSubmit}
        >
          <label className="block text-sm font-medium" htmlFor="email">
            Email
          </label>
          <input
            className="mt-2 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-neutral-900"
            id="email"
            autoComplete="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label className="mt-4 block text-sm font-medium" htmlFor="password">
            Password
          </label>
          <input
            className="mt-2 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-neutral-900"
            id="password"
            autoComplete="current-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error ? (
            <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          ) : null}

          <button
            className="mt-5 w-full rounded-md bg-neutral-950 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Logging in...' : 'Log in'}
          </button>
        </form>

        <p className="text-sm text-neutral-600">
          No account?{' '}
          <Link className="font-medium text-neutral-950 underline" to="/register">
            Register
          </Link>
        </p>
      </section>
    </main>
  )
}
