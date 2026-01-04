FROM nginx:alpine

# Copy the frontend files to nginx html directory
COPY . /usr/share/nginx/html

# Expose port 80 (nginx default)
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]