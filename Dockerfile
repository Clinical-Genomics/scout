FROM node:14.0.0-alpine

ARG PORT

# create destination directory
RUN mkdir -p /app
WORKDIR /app

ENV PATH /scout-react/node_modules/.bin:$PATH

# update and install dependency
RUN apk update && apk upgrade
RUN apk add git
RUN apk add curl

# copy the app, note .dockerignore
COPY package.json ./
COPY yarn.lock ./
RUN yarn install
COPY . .

EXPOSE $PORT
CMD [ "yarn", "start" ]
