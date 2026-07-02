# Build stage
FROM node:22-alpine AS BUILD

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files (Note le AS BUILD en majuscules ici aussi)
COPY --from=BUILD /app/dist /usr/share/nginx/html

# Nettoyage et copie de ta configuration
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]