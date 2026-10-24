# Dev-oriented image used by docker-compose. Production frontend is a static
# Vite build served by Vercel (see docs/08-deployment.md).
FROM node:22-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
