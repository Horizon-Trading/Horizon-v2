import { NextResponse, type NextRequest } from "next/server";
import { timingSafeEqual } from "node:crypto";

export function proxy(request: NextRequest) {
  const password=process.env.DASHBOARD_PASSWORD;
  if(process.env.APP_ENV==="production" && (!password || password.length<16 || !process.env.HORIZON_API_TOKEN)) {
    return new NextResponse("Dashboard access is not configured",{status:503});
  }
  if(!password) return NextResponse.next();
  const expected=Buffer.from("Basic "+Buffer.from((process.env.DASHBOARD_USER || "horizon")+":"+password).toString("base64"));
  const received=Buffer.from(request.headers.get("authorization") || "");
  if(received.length===expected.length && timingSafeEqual(received,expected)) return NextResponse.next();
  return new NextResponse("Authentication required",{status:401,headers:{"WWW-Authenticate":"Basic realm=\"Horizon\", charset=\"UTF-8\""}});
}
export const config={matcher:["/((?!_next/static|_next/image|favicon.ico).*)"]};
