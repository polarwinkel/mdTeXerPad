# mdTeXerPad
Multi-User live-rendering Editor for Markdown with included LaTeX-Formulas

## What is this?

![Screenshot of mdTeXerPad](mdTeXerPad.png)

On the left side you can type a mixture of Markdown with LaTeX-Formulas included.

You, as well as all other users on the site, will see the on-time rendering on the right.

## How to use this

### The native local way

- clone the repository or download this
- make sure you have `python3-markdown` and `python3-websockets` installed
- Run the `mdTeXerPad.py`
- point your Browser to `localhost:8081` and start to mdTeXing!
    - mdTeXerPad will also be available from your local network, you can change this by setting `onlyLocal = True` in the `mdTeXerPad.py`!

### The Docker way

- clone the repository or download this
- run `docker-compose up -d`
- point your browser to port `8081` of your docker-host, i.e. `127.0.0.1:8081`

### Getting it to the web

I recommend using a reverse proxy like nginx, you need to make sure that port `8081` (http) and `8082` (ws) is available.

This config will do:

```
server {
    listen 80;
    listen [::]:80;
    server_name <your.tld>;
    location / {
        proxy_set_header        REMOTE_USER         $remote_user;
        proxy_set_header        Host                $host;
        proxy_pass http://<your-ip>:8081/;
    }
}
server {
    listen 8082;
    listen [::]:8082;
    server_name <your.tld>;
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://<your-ip>:8082/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Make sure you replace the stuff in the angle brackets `<your ..>`!

And be sure to **forward the port `8082` in your router**!

You can then have nginx limit access, encrypt the traffic etc.

## Limitations

This is intended for small use only!

- There is **just one Pad** to work on
- the code is definitely **not optimized for fast execution**
- it is developed **only for Firefox** (uses MathML for LaTeX-Formulas)
- it is **not checked for security issues**, be sure to restrict access to trusted persons!

If you need it bigger feel free to fork and change this or commit a pull-request.
