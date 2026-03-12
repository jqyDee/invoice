# Stage 1: Build frontend
FROM node:20-alpine AS builder

WORKDIR /app

# Copy frontend source
COPY openapi.json routes.ts index.html package.json package-lock.json vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json openapi-ts.config.ts ./
COPY src ./src
COPY public ./public

# Install deps and build
RUN npm ci
RUN npm run build

# Stage 2: Serve with Nginx / production
FROM nginx:alpine AS prod
# Copy build output to Nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom Nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Stage 2: Serve with Nginx / development
FROM node:20-alpine AS dev
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run openapi-ts:generate
EXPOSE 5273
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
