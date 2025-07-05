FROM node:24-alpine AS code
RUN mkdir /app
WORKDIR /app
COPY package.json package-lock.json .
RUN mkdir public && mkdir src
COPY public public
COPY src src
RUN npm install && npm run build

FROM node:24-alpine
RUN npm install -g serve && mkdir /app
WORKDIR /app
COPY --from=code /app/build /app
EXPOSE 3000
CMD ["serve", "-s", "."]
