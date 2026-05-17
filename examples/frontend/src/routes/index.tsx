import { authClient } from "#/lib/auth-client";
import { Link, createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  const { data: session, isPending, refetch } = authClient.useSession();

  async function handleSignOut() {
    await authClient.signOut();
    await refetch();
  }

  const handleClick = async () => {
    const { data } = await authClient.token();
    if (!data?.token) {
      return;
    }
    const { token } = data;

    const response = await fetch("http://127.0.0.1:8000", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }).then((res) => res.json());

    console.log(response);
  };

  return (
    <main className="min-h-screen bg-neutral-50 px-6 py-12 text-neutral-950">
      <button onClick={handleClick}>Send Request</button>
      <section className="mx-auto flex w-full max-w-xl flex-col gap-6">
        <div>
          <h1 className="text-3xl font-semibold">Better Auth SQLite Demo</h1>
          <p className="mt-2 text-sm text-neutral-600">
            Local email and password auth backed by SQLite.
          </p>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          {isPending ? (
            <p className="text-sm text-neutral-600">Loading session...</p>
          ) : session ? (
            <div className="flex flex-col gap-4">
              <div>
                <p className="text-sm font-medium">Signed in as</p>
                <p className="mt-1 text-sm text-neutral-600">
                  {session.user.name} - {session.user.email}
                </p>
              </div>
              <button
                className="w-fit rounded-md border border-neutral-300 px-4 py-2 text-sm font-medium hover:bg-neutral-100"
                onClick={handleSignOut}
                type="button"
              >
                Sign out
              </button>
            </div>
          ) : (
            <div className="flex flex-wrap gap-3">
              <Link
                className="rounded-md bg-neutral-950 px-4 py-2 text-sm font-medium text-white"
                to="/login"
              >
                Log in
              </Link>
              <Link
                className="rounded-md border border-neutral-300 px-4 py-2 text-sm font-medium hover:bg-neutral-100"
                to="/register"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
