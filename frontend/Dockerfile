# =========================================================
# Dockerfile - Frontend Playnalyze (React + Vite)
# Simpan file ini sebagai: frontend/Dockerfile
# Multi-stage build: build assets statis, lalu serve pakai Nginx (ringan, hemat RAM)
# =========================================================

# ---- Stage 1: Build ----
FROM node:20-alpine AS build

WORKDIR /app

# Copy file dependency dulu untuk caching layer
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code lalu build
COPY . .
RUN npm run build
# Hasil build Vite ada di folder /app/dist

# ---- Stage 2: Serve dengan Nginx ----
FROM nginx:alpine

# Hapus konfigurasi default Nginx, ganti dengan konfigurasi custom (lihat nginx.conf)
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
