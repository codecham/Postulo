import type { NextConfig } from "next";

// Content Security Policy, production only: `next dev` needs eval and a websocket for
// hot reload. Next.js inlines small scripts and styles, hence 'unsafe-inline'; every
// other source (external scripts, frames, plugins, form targets) is blocked.
const contentSecurityPolicy = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self'",
  "connect-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join("; ");

const productionHeaders =
  process.env.NODE_ENV === "production"
    ? [{ key: "Content-Security-Policy", value: contentSecurityPolicy }]
    : [];

const nextConfig: NextConfig = {
  // Self-contained server in .next/standalone: small Docker image, no node_modules
  output: "standalone",
  poweredByHeader: false,
  cacheComponents: true,
  partialPrefetching: true,
  experimental: {
    serverActions: {
      // Room for a 5 MB CV upload (the default limit is 1 MB)
      bodySizeLimit: "6mb",
    },
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          ...productionHeaders,
        ],
      },
    ];
  },
};

export default nextConfig;
