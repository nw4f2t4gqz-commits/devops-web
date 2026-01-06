Docker quick start

Build image locally for MacOS:

```bash
cd /path/to/project
docker build -t devops-web:latest .

```

Build image for AMD64 and push to docker.hub

```bash
docker buildx build --platform linux/amd64 -t jartas/devops-web:linux-amd64 --push .
```

Run container:

```bash
docker run --rm -p 5001:5001 --name devops-web devops-web:latest
```

Or with docker-compose:

```bash
docker-compose up --build
```

Notes:
- App listens on port 5001 by default (you can override with `PORT` env).
- Logs are written to `log/app.log` inside the container; we also expose logs through container stdout.
- For production consider running behind a WSGI server (gunicorn) and using multi-stage builds / smaller base image.
 - To enable contact form email sending via SMTP (Office365), set the following environment variables in your container or host:
	 - SMTP_HOST (e.g. smtp.office365.com)
	 - SMTP_PORT (e.g. 587)
	 - SMTP_USER (your SMTP username / email)
	 - SMTP_PASS (SMTP password)
	 - EMAIL_TO (destination address for incoming leads)

 Example docker-compose snippet to set env:

 ```yaml
 services:
	 web:
		 build: .
		 environment:
			 - SMTP_HOST=smtp.office365.com
			 - SMTP_PORT=587
			 - SMTP_USER=you@example.com
			 - SMTP_PASS=${SMTP_PASS}
			 - EMAIL_TO=you@example.com
 ```
