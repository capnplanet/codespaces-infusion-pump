import { SignJWT } from "jose";

export async function generateDevJwt(params: {
  subject: string;
  roles: string[];
  secret: string;
  ttlMinutes: number;
}): Promise<string> {
  const { subject, roles, secret, ttlMinutes } = params;
  const now = Math.floor(Date.now() / 1000);
  return await new SignJWT({ roles })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setSubject(subject)
    .setIssuedAt(now)
    .setExpirationTime(now + ttlMinutes * 60)
    .sign(new TextEncoder().encode(secret));
}
