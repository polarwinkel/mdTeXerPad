# mdTeXerPad
Multi-User live-rendering Editor for Markdown with included LaTeX-Formulas

## What is this?

![Screenshot of mdTeXerPad](mdTeXerPad.png)

On the left side you can type a mixture of Markdown with LaTeX-Formulas included.

You, as well as all other users on the site, will see the on-time rendering on the right.

## How to use this

### The native local way

- clone the repository or download this
- make sure you have the dependencies installed as listed in the `Dockerfile`
- Run it by either
    - executing `gunicorn3 -k flask_sockets.worker --bind 0.0.0.0:8000 app:app` (the performance-option)
    - or `python3 app.py` (development-option, will be port 5000 then)
- point your Browser to `localhost:8000` and start to mdTeXing!
    - mdTeXerPad will also be available from your local network, you can change this by setting `onlyLocal = True` in the `mdTeXerPad.py`!

It will _not_ run on Debian Buster and Ubuntu 20.04 without getting the dependencies from pip since some dependencies in apt are missing (Debian Buster) or broken (Ubuntu 20.04). Debian Bullseye is fine!

### The Docker way

- clone the repository or download this
- run `docker-compose up -d`
- point your browser to port `8000` of your docker-host, i.e. `127.0.0.1:8000`

### Getting it to the web

I recommend using a reverse proxy like nginx, i.e. to add encryption. ýou need to make sure that port `8000` is available.

This config will do for nginx, adapt to your needs:

```
server {
    listen 80;
    listen [::]:80;
    server_name <your.tld>;
    location / {
        # any path for the location like ´/mtp/´ is fine as well
        proxy_pass              http://localhost:8000/; # The / is important!
        proxy_set_header        Host            $host;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Remote-User $remote_user;
        proxy_http_version 1.1;
        proxy_connect_timeout 2h;
        proxy_send_timeout 2h;
        proxy_read_timeout 2h;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

Make sure you replace the stuff in the angle brackets `<your ..>`!

You can then have nginx limit access, encrypt the traffic etc.

## Limitations

This is intended for the use with a school class in one lesson and is tested for up to 30 users and pads with ~100 lines of code.

- There is **just one Pad** to work on (so far...)
- only one person at a time should/can edit
- it is developed **only for Firefox** (uses MathML for LaTeX-Formulas) **Edge/Chrome won't render formulas correctly**
- it is **not checked for security issues**, be sure to restrict access to trusted persons and(/or) run the docker version for isolation/sandboxing!

If you need it bigger feel free to fork and change this or commit a pull-request.

## You need just a Markdown-LaTeX-to-HTML-converter for your own project?

Just grab the `mdTeX2html.py` from the `modules`-folder and the `latex2mathml` from [Ronie Martinez](https://github.com/roniemartinez/latex2mathml) which you find in pip as well. Thanks for this, Ronie!
