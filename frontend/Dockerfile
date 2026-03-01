FROM node:24-alpine

WORKDIR /app

# install deps
COPY package.json package-lock.json ./
RUN npm ci

# copy app
COPY . .

EXPOSE 3202

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
