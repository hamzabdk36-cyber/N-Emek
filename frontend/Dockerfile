# N-Emek arayuzu: derle, sonra nginx ile sun.
#
# Iki asamali: node yalnizca derleme icin gerekli, calisan imajda
# bulunmuyor. Sonuc imaj ~50 MB.

FROM node:24-alpine AS derleme
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=derleme /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
