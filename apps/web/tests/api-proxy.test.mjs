import assert from "node:assert/strict";
import { test } from "node:test";
import { GET } from "../app/api/[...path]/route.ts";

test("runtime binding preserves base path/query and keeps credentials server-side", async () => {
  const previous = { ...process.env };
  const originalFetch = globalThis.fetch;
  try {
    process.env.APP_ENV = "production";
    process.env.HORIZON_API_URL = "https://bound.example/internal/api/";
    process.env.API_INTERNAL_URL = "https://unused.example";
    process.env.HORIZON_API_TOKEN = "test-server-token";
    let calls = 0;
    globalThis.fetch = async (url, options) => {
      calls++;
      assert.equal(url.href, "https://bound.example/internal/api/signals?limit=10&offset=20");
      assert.equal(options.headers["x-horizon-token"], "test-server-token");
      assert.equal(options.cache, "no-store");
      assert.equal(options.redirect, "error");
      return Response.json({ detail: "Unauthorized" }, { status: 401 });
    };
    const request = { nextUrl: new URL("https://dashboard.example/api/signals?limit=10&offset=20") };
    const params = { params: Promise.resolve({ path: ["signals"] }) };
    const response = await GET(request, params);
    assert.equal(response.status, 401);
    assert.equal(response.headers.get("x-horizon-token"), null);
    assert.deepEqual(await response.json(), { detail: "Unauthorized" });
    delete process.env.HORIZON_API_URL;
    delete process.env.API_INTERNAL_URL;
    assert.equal((await GET(request, params)).status, 503);
    assert.equal(calls, 1);
    assert.equal((await GET(request, { params: Promise.resolve({ path: ["admin"] }) })).status, 404);
    assert.equal(calls, 1);
    process.env.API_INTERNAL_URL = "http://api:8000";
    globalThis.fetch = async (url) => {
      assert.equal(url.href, "http://api:8000/signals?limit=10&offset=20");
      return Response.json([]);
    };
    assert.equal((await GET(request, params)).status, 200);
  } finally {
    globalThis.fetch = originalFetch;
    for (const key of ["APP_ENV", "HORIZON_API_URL", "API_INTERNAL_URL", "HORIZON_API_TOKEN"]) {
      if (previous[key] === undefined) delete process.env[key];
      else process.env[key] = previous[key];
    }
  }
});
