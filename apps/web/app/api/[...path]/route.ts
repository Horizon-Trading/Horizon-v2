import type { NextRequest } from "next/server";

export async function GET(request: NextRequest, { params }: { params: Promise<{path:string[]}> }) {
  const { path }=await params;
  if (!path.length || !["health","ready","status","news","signals","portfolio"].includes(path[0])) {
    return Response.json({detail:"Not found"},{status:404});
  }
  const base=process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  try {
    const response=await fetch(base.replace(/\/$/,"")+"/"+path.map(encodeURIComponent).join("/")+request.nextUrl.search,{
      headers:{"x-horizon-token":process.env.HORIZON_API_TOKEN || ""},cache:"no-store",signal:AbortSignal.timeout(15000),redirect:"error",
    });
    return new Response(await response.text(),{status:response.status,headers:{"Content-Type":"application/json","Cache-Control":"no-store"}});
  } catch {
    return Response.json({detail:"API unavailable"},{status:503});
  }
}
