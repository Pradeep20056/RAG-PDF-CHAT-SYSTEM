# Base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy all frontend code
COPY . .

# Build React app
RUN npm run build

# Serve the build folder using a lightweight web server
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Run the frontend
CMD ["serve", "-s", "dist", "-l", "3000"]
