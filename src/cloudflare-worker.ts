const BACKEND_PATHS = [
  "/api/",
  "/docs",
  "/redoc",
  "/openapi.json",
  "/robots.txt",
  "/sitemap.xml",
  "/manifest.webmanifest",
  "/ads.txt",
] as const;

function shouldProxy(pathname: string): boolean {
  return BACKEND_PATHS.some((path) =>
    path.endsWith("/") ? pathname.startsWith(path) : pathname === path || pathname.startsWith(`${path}/`),
  );
}

async function proxyToBackend(request: Request, env: Env): Promise<Response> {
  const incomingUrl = new URL(request.url);
  const backendUrl = new URL(env.BACKEND_ORIGIN);
  backendUrl.pathname = incomingUrl.pathname;
  backendUrl.search = incomingUrl.search;

  const headers = new Headers(request.headers);
  headers.set("X-Forwarded-Host", incomingUrl.host);
  headers.set("X-Forwarded-Proto", incomingUrl.protocol.replace(":", ""));

  const clientIp = request.headers.get("CF-Connecting-IP");
  if (clientIp) {
    headers.set("X-Forwarded-For", clientIp);
  }

  return fetch(
    new Request(backendUrl, {
      method: request.method,
      headers,
      body: request.body,
      redirect: "manual",
    }),
  );
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    try {
      if (shouldProxy(url.pathname)) {
        return await proxyToBackend(request, env);
      }

      return await env.ASSETS.fetch(request);
    } catch (error) {
      console.error(
        JSON.stringify({
          message: "edge_request_failed",
          path: url.pathname,
          error: error instanceof Error ? error.message : "Unknown error",
        }),
      );
      return Response.json({ detail: "Layanan sementara tidak tersedia" }, { status: 502 });
    }
  },
} satisfies ExportedHandler<Env>;
