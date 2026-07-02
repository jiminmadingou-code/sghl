# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Nettoyage de sécurité pour enlever le dossier/fichier default.conf qui buggue
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copie de ton fichier nginx.conf au BON endroit (dans conf.d)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]