ARG NODE_VERSION=21

FROM node:${NODE_VERSION}-alpine

COPY package.json yarn.lock /service/

COPY src /service/src

WORKDIR /service

RUN yarn install --frozen-lockfile

EXPOSE 8000

CMD ["yarn", "start"]
