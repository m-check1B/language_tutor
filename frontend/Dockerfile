# Build stage
FROM node:16 as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:16-alpine

WORKDIR /app

# Copy built assets from the build stage
COPY --from=build /app/package.json .
COPY --from=build /app/package-lock.json .
COPY --from=build /app/.svelte-kit ./.svelte-kit
COPY --from=build /app/node_modules ./node_modules

# Expose the port the app runs on
EXPOSE 3081

# Start the application
CMD ["node", ".svelte-kit/output/server/index.js"]
