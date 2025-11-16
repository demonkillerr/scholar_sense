# Frontend Dockerfile for ScholarSense - Simplified Production Build
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install || npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start Next.js
CMD ["npm", "run", "start"]
