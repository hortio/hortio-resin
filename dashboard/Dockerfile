
FROM arm32v7/nginx:mainline
COPY build/ /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY certs/cert.key.pem /etc/nginx/cert.key.pem
COPY certs/cert.pem /etc/nginx/cert.pem
EXPOSE 443
CMD ["nginx", "-g", "daemon off;"]