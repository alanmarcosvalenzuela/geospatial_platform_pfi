# build env
FROM node:20.9.0-alpine as build
WORKDIR /app

# Clone the GitHub repository
RUN git clone https://github.com/alanmarcosvalenzuela/geospatial_platform_pfi.git .

# Change the working directory to "frontend"
WORKDIR /app/frontend

RUN yarn add react-leaflet

RUN yarn add leaflet-draw

RUN yarn add @react-leaflet/core


RUN yarn

RUN yarn build

# production env
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]