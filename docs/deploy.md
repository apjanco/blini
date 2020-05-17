How to deploy blini with Docker


1. Click on the "Use this Template" button an create a new respostory based on blini. From your repostory get the clone link and then `git clone https://github.com/<you>/your_blini.git`
2. Update `url: "blini.apjan.co"` in `/app/site/site.yaml` this should name the domain you'll deploy the app to.
3. Run `docker build -t blini .` from the directory containing Dockerfile.
4. create a directory to contain ssl certs ```cd && mkdir certs``` ([src](https://cloud.google.com/community/tutorials/nginx-reverse-proxy-docker))
5. create an nginx proxy container:  
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
6.  run the Let's Encrypt companion container:
```
docker run -d \
    --name nginx-letsencrypt \
    --volumes-from nginx-proxy \
    -v $HOME/certs:/etc/nginx/certs:rw \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    jrcs/letsencrypt-nginx-proxy-companion
```
7. now start the blini container:
```
docker run -d \
    --name blini \
    -e 'LETSENCRYPT_EMAIL=ajanco@haverford.edu' \
    -e 'LETSENCRYPT_HOST=blini.apjan.co' \
    -e 'VIRTUAL_HOST=blini.apjan.co' blini
```
