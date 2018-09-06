# build environment
FROM node:8-alpine as builder
RUN mkdir /app
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json /app/package.json
COPY yarn.lock /app/yarn.lock
RUN npm install yarn
RUN yarn
COPY . /app
RUN yarn build

# production environment
FROM arm32v7/nginx:mainline
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY certs/cert.key.pem /etc/nginx/cert.key.pem
COPY certs/cert.pem /etc/nginx/cert.pem
EXPOSE 443
CMD ["nginx", "-g", "daemon off;"]