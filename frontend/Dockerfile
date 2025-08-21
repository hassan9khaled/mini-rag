# Use official Node.js base image (lightweight version)
FROM node:22-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY /package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your code
COPY . .

# Expose the port your app uses (change if not 5173)
EXPOSE 5173

# Command to run your app (e.g., npm run dev)
CMD [ "npm", "run", "dev", "--", "--host", "0.0.0.0" ]