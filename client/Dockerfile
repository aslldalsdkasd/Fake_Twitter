FROM nginx

RUN  rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY /client/dist /app/dist

COPY /client/nginx.conf /etc/nginx/nginx.conf