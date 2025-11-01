# ----------------------------------------------------------------------
# Stage 1: Build Stage (Handles Dependencies)
# ----------------------------------------------------------------------
FROM node:18-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy dependency definition files
# This step is cached as long as package.json/package-lock.json don't change
COPY package.json package-lock.json /app/

# Install dependencies
RUN npm install

# Copy all source files
COPY . /app

# ----------------------------------------------------------------------
# Stage 2: Production/Runtime Stage (Minimal Image)
# ----------------------------------------------------------------------

FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy *only* the production dependencies and built application files
COPY --from=builder /app/node_modules /app/node_modules

# Copy the application source code (or built artifacts)
COPY --from=builder /app /app

# Expose the port the server runs on
EXPOSE 8080

# Run the application
CMD ["npm", "run", "serve"]
