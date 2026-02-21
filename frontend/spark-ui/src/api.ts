export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: string; status?: number };

export async function apiRequest<T>(params: {
  baseUrl: string;
  path: string;
  method?: "GET" | "POST";
  token?: string;
  body?: unknown;
}): Promise<ApiResult<T>> {
  const { baseUrl, path, method = "GET", token, body } = params;
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: body === undefined ? undefined : JSON.stringify(body)
    });

    const isJson = response.headers.get("content-type")?.includes("application/json") ?? false;
    const payload = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const detail = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
      return { ok: false, error: detail, status: response.status };
    }

    return { ok: true, data: payload as T };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Unknown network error" };
  }
}
