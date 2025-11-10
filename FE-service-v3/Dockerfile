FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port 5175
EXPOSE 5175

# Run dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5175"]
