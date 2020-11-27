FROM node:14.0.0

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY cp-frontend/package.json /app/package.json
RUN npm install
RUN npm install -g @angular/cli@11.0.2

COPY ./cp-frontend/ /app

CMD ng serve --host 0.0.0.0
