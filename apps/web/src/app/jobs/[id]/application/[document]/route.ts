import { api } from "@/lib/api/client";
import { isDocumentName } from "@/lib/applications/types";
import { getAuthHeaders } from "@/lib/auth/session";

/**
 * Download a PDF of the application. The browser cannot call the API itself (the
 * access token stays in an httpOnly cookie), so this route fetches it and passes it on.
 */
export async function GET(
  _request: Request,
  { params }: RouteContext<"/jobs/[id]/application/[document]">,
) {
  const { id, document } = await params;
  const headers = await getAuthHeaders();
  if (!headers) {
    return new Response("Not logged in", { status: 401 });
  }
  if (!isDocumentName(document)) {
    return new Response("Not found", { status: 404 });
  }
  const path =
    document === "cv.pdf"
      ? "/job-search/matches/{match_id}/application/cv.pdf"
      : "/job-search/matches/{match_id}/application/cover-letter.pdf";
  const result = await api.GET(path, {
    headers,
    params: { path: { match_id: id } },
    parseAs: "blob",
  });
  if (!result.response.ok || !result.data) {
    return new Response("Not found", { status: result.response.status });
  }
  return new Response(result.data, {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition":
        result.response.headers.get("Content-Disposition") ?? "attachment",
    },
  });
}
