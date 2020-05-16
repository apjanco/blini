How to deploy blini with Docker


1. Clone this template `git clone https://github.com/apjanco/blini.git`
2. Run `docker build -t blini .` from the directory containing Dockerfile.
3. create a directory to contain ssl certs ```cd && mkdir certs``` ([src](https://cloud.google.com/community/tutorials/nginx-reverse-proxy-docker))
4. create an nginx proxy container:  
```
docker run -d -p 80:80 -p 443:443 \
    --name nginx-proxy \
    -v $HOME/certs:/etc/nginx/certs:ro \
    -v /etc/nginx/vhost.d \
    -v /usr/share/nginx/html \
    -v /var/run/docker.sock:/tmp/docker.sock:ro \
    --label com.github.jrcs.letsencrypt_nginx_proxy_companion.nginx_proxy=true \
    jwilder/nginx-proxy
```
5.  run the Let's Encrypt companion container:
```
docker run -d \
    --name nginx-letsencrypt \
    --volumes-from nginx-proxy \
    -v $HOME/certs:/etc/nginx/certs:rw \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    jrcs/letsencrypt-nginx-proxy-companion
```
6. now start the blini container:
```
docker run -d \
    --name blini \
    -e 'LETSENCRYPT_EMAIL=you@haverford.edu' \
    -e 'LETSENCRYPT_HOST=blini.haverford.edu' \
    -e 'VIRTUAL_HOST=blini.haverford.edu' blini
```
