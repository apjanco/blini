How to deploy blini with Docker


1. Clone this template `git clone https://github.com/apjanco/blini.git`
2. Run `docker build -t myimage .` from the directory containing Dockerfile.
3. create a directory to contain ssl certs ```cd && mkdir certs``` ([src](https://cloud.google.com/community/tutorials/nginx-reverse-proxy-docker))
