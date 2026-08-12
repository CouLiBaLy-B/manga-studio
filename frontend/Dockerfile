FROM node:20-alpine AS base

ARG BACKEND_URL=http://127.0.0.1:8000
ENV BACKEND_URL=${BACKEND_URL}

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . ./
RUN npm run build

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["npm", "run", "start"]
