# Deploying Lagrange-Lock to `lagrange.shreyashrai.com`

This deploys the Phase 3 server (physics + PPO inference + Three.js frontend) to a
small Linux VPS, behind Caddy for automatic HTTPS. Total cost: free (Oracle Cloud
Always Free) to ~€4/mo (Hetzner). Pick any subdomain — `lagrange` is just the example.

The frontend uses relative URLs, so once the server is reachable at the domain,
the whole app (including "RUN AI") works with no code changes.

---

## What you need

- A VPS with a public IP (Hetzner CX22, Oracle Cloud Always Free, DigitalOcean, etc.).
  Aim for **≥ 1 GB RAM** — PPO inference loads PyTorch.
- `shreyashrai.com` managed at some DNS provider (Cloudflare, Namecheap, GoDaddy…).
- Docker + the Compose plugin on the VPS.

---

## Step 1 — Point the subdomain at the server

In your DNS provider, add **one** record:

| Type | Name        | Value (Content)        | Proxy / TTL |
|------|-------------|------------------------|-------------|
| A    | `lagrange`  | `<your VPS public IP>` | DNS-only / Auto |

> If your domain is on **Cloudflare**, set the record to **DNS only** (grey cloud),
> *not* proxied (orange cloud), so Caddy can complete the Let's Encrypt challenge.
> You can switch it back to proxied later once HTTPS works.

Verify before continuing (should print your VPS IP):

```bash
dig +short lagrange.shreyashrai.com
```

---

## Step 2 — Install Docker on the VPS

SSH in, then:

```bash
curl -fsSL https://get.docker.com | sh
```

Log out/in once so your user can run Docker without sudo (optional).

---

## Step 3 — Get the code and launch

```bash
git clone -b deploy https://github.com/ItsMat78/Lagrange-Lock.git
cd Lagrange-Lock

# Build the app image and start app + Caddy. Caddy auto-issues the TLS cert.
DOMAIN=lagrange.shreyashrai.com docker compose up -d --build
```

First build takes a few minutes (PyTorch CPU wheel). When it finishes:

```bash
docker compose ps          # both services "running"
docker compose logs -f caddy   # watch the certificate get issued
```

Open **https://lagrange.shreyashrai.com/realtime_viewer.html** 🎉

---

## Updating after you push changes

```bash
cd Lagrange-Lock
git pull
DOMAIN=lagrange.shreyashrai.com docker compose up -d --build
```

## Useful commands

```bash
docker compose logs -f app     # server / AI inference logs
docker compose restart app     # restart just the app
docker compose down            # stop everything
```

---

## Notes / caveats

- **Open firewall ports 80 and 443** on the VPS (and in the cloud provider's
  security group — this is the #1 gotcha on Oracle/AWS). Caddy needs 80 for the
  ACME challenge and 443 for HTTPS.
- The server uses Python's single-threaded `http.server`, so it handles one request
  at a time. Fine for a portfolio demo; if it ever needs concurrency, the next step
  would be moving the handlers into a WSGI/ASGI app (Flask/FastAPI) behind gunicorn.
- AI runs are CPU-bound (20 sims per request). Expect a few seconds per "RUN AI" on
  a small VPS — that's the inference, not the network.
- Models live in `phase_3/models/` and are baked into the image at build time.
```
