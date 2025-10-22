# Use Node.js LTS
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Build the React app
RUN npm run build

# Use a lightweight server to serve the build
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Serve the build folder
CMD ["serve", "-s", "build", "-l", "3000"]
