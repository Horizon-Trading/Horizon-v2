FROM node:22-bookworm-slim AS build
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web ./
RUN npm run lint && npm run build -- --webpack

FROM node:22-bookworm-slim
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
WORKDIR /app
COPY --from=build --chown=node:node /app/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build --chown=node:node /app/apps/web/public ./apps/web/public
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD node -e "fetch('http://127.0.0.1:3000').then(r=>process.exit(r.status<500?0:1)).catch(()=>process.exit(1))"
CMD ["node", "apps/web/server.js"]
