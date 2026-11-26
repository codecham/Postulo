import { connection } from "next/server";

import { api } from "@/lib/api/client";

/** Shows whether the API and its database answer. Rendered on each request. */
export async function ApiStatus() {
  await connection(); // render at request time, never at build time
  const healthy = await api.GET("/health/db").then(
    ({ response }) => response.ok,
    () => false, // network error: the API is not reachable
  );

  return (
    <p className="text-muted flex items-center gap-2 text-xs">
      <span
        aria-hidden
        className={`size-2 rounded-full ${healthy ? "bg-success" : "bg-danger"}`}
      />
      {healthy ? "All systems operational" : "API or database unreachable"}
    </p>
  );
}
