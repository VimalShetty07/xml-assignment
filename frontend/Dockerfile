FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# Vite dev server; proxies /jobs to the api service when DOCKER=true.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
