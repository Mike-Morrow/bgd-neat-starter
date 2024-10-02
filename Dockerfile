# Use Node.js as base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install both dependencies and devDependencies
# --include=dev ensures that devDependencies are installed as well
RUN npm install --include=dev

# Copy the rest of the project files to the container
COPY . .

# Expose port 8080 for Browsersync
EXPOSE 8080

# Set the environment to development (optional but useful to avoid production-specific behaviors)
ENV NODE_ENV development

# Set the command to run your start script
CMD ["npm", "start"]

