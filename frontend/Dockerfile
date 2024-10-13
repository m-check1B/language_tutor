# Use an official Node runtime as a parent image
FROM node:16 as builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the current directory contents into the container at /app
COPY . .

# Build the app
RUN npm run build

# Start a new stage for a smaller production image
FROM node:16-slim

# Set the working directory in the container
WORKDIR /app

# Copy built assets from builder stage
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .
COPY --from=builder /app/node_modules ./node_modules

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the app when the container launches
CMD ["node", "build"]
