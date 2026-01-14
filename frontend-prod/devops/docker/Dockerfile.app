ARG BASE_IMAGE

FROM $BASE_IMAGE AS BUILDER

ARG REACT_APP_API_URL

WORKDIR /code

COPY . .

RUN echo "REACT_APP_API_URL=$REACT_APP_API_URL" > .env

RUN npm run build

RUN date '+%F-%H:%M:%S' > build.timestamp

FROM node:18.15.0-alpine

ENV NODE_ENV production

RUN npm install -g serve

RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 app && \
    mkdir /app && \
    chown app:node /app

USER app

WORKDIR /app

COPY --from=BUILDER --chown=app:node /code/build ./build
COPY --from=BUILDER --chown=app:node /code/public ./public
COPY --from=BUILDER --chown=app:node /code/node_modules ./node_modules
COPY --from=BUILDER --chown=app:node /code/build.timestamp  .

ENTRYPOINT [ "serve" ]
CMD [ "-s", "build" ]
