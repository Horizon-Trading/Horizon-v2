import type { NextRequest } from "next/server";

export async function GET(request: NextRequest, { params }: { params: Promise<{path:string[]}> }) {
  const { path }=await params;
  if (!path.length || !["health","ready","status","news","signals","portfolio"].includes(path[0])) {
    return Response.json({detail:"Not found"},{status:404});
  }
  try {
    // Vercel injects this binding at function runtime, not during build/middleware.
    const base = process.env.HORIZON_API_URL || process.env.API_INTERNAL_URL
      || (process.env.APP_ENV !== "production" ? "http://127.0.0.1:8000" : undefined);
    if (!base) return Response.json({detail:"API is not configured"},{status:503});
    const target = new URL(path.map(encodeURIComponent).join("/"), base.replace(/\/$/, "") + "/");
    target.search = request.nextUrl.search;
    const response=await fetch(target,{
      headers:{"x-horizon-token":process.env.HORIZON_API_TOKEN || ""},cache:"no-store",signal:AbortSignal.timeout(15000),redirect:"error",
    });
    return new Response(await response.text(),{status:response.status,headers:{"Content-Type":"application/json","Cache-Control":"no-store"}});
  } catch {
    return Response.json({detail:"API unavailable"},{status:503});
  }
}
