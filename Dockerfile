FROM node:20-alpine AS builder

WORKDIR /app

# Copy lockfile + package.json (cache deps)
COPY package*.json ./

# Clean install (full deps including dev)
RUN npm ci

# Copy source + build
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /usr/src/app

ENV NODE_ENV=production

# Copy package + prod install
COPY package*.json ./
RUN npm ci --omit=dev --no-optional && npm cache clean --force

# Copy built assets
COPY --from=builder /app/build ./build

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S bunkerbuster -u 1001
USER bunkerbuster

EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => process.exit(r.statusCode !== 200 ? 1 : 0))"

CMD ["npm", "run", "prod"]
