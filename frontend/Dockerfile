# Leon frontend — build then serve the static bundle (demo scale, [500]).
FROM node:22-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:22-slim AS serve
WORKDIR /app
RUN npm install -g vite@6.0.7
COPY --from=build /app/dist ./dist
EXPOSE 5173
CMD ["vite", "preview", "--host", "0.0.0.0", "--port", "5173"]
