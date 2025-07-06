FROM node:24-alpine
RUN mkdir /app
WORKDIR /app
COPY package.json package-lock.json .
RUN npm install
RUN mkdir public && mkdir src
COPY public public
COPY src src
CMD ["npm", "start"]
