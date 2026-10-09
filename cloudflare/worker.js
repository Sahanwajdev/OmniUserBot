/**
 * Cloudflare Worker Gateway for OmniUserBot
 * - Serves edge health check endpoints
 * - Proxies traffic to the underlying container
 * - Runs cron keep-alive pings every 5 minutes to prevent idle sleeping
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Root status dashboard
    if (url.pathname === "/" || url.pathname === "/status") {
      const statusData = {
        status: "online",
        service: env.SERVICE_NAME || "OmniUserBot",
        cloudflare_edge: true,
        region: request.cf ? request.cf.colo : "GLOBAL",
        timestamp: new Date().toISOString(),
        message: "OmniUserBot Cloudflare Gateway is active and healthy."
      };

      return new Response(JSON.stringify(statusData, null, 2), {
        headers: {
          "content-type": "application/json; charset=utf-8",
          "cache-control": "no-cache"
        }
      });
    }

    // Health probe for monitoring services
    if (url.pathname === "/health" || url.pathname === "/ping") {
      return new Response("OK", {
        status: 200,
        headers: { "content-type": "text/plain" }
      });
    }

    // Proxy other requests to the container if container binding is active
    if (env.CONTAINER) {
      try {
        return await env.CONTAINER.fetch(request);
      } catch (err) {
        return new Response(`Container Proxy Error: ${err.message}`, { status: 502 });
      }
    }

    return new Response("Not Found", { status: 404 });
  },

  // Automated Cloudflare Cron Trigger (Runs every 5 mins)
  async scheduled(event, env, ctx) {
    console.log(`[Cloudflare Cron] Keep-alive trigger executed at ${new Date().toISOString()}`);
    if (env.TARGET_URL) {
      try {
        const res = await fetch(`${env.TARGET_URL}/health`);
        console.log(`[Cloudflare KeepAlive] Target ping status: ${res.status}`);
      } catch (e) {
        console.error(`[Cloudflare KeepAlive] Ping error: ${e.message}`);
      }
    }
  }
};
