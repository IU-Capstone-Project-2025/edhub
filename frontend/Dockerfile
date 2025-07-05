FROM node:24-alpine
RUN mkdir /app
WORKDIR /app
COPY package.json package-lock.json .
RUN mkdir public && mkdir src
COPY public public
COPY src src
RUN npm install
CMD ["npm", "start"]
