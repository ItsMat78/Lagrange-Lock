# Deploying Lagrange-Lock to `lagrange-lock.shreyashrai.com` (free, always-on)

This hosts the Phase 3 server (physics + PPO inference + Three.js frontend) on a
free **Oracle Cloud "Always Free"** VM, behind Caddy for automatic HTTPS, with the
subdomain managed at **Namecheap**. Cost: **$0 forever**, and it stays up when your
own machine is off.

The frontend uses relative URLs, so once the server is reachable at the domain the
whole app (including "RUN AI") works with no code changes.

---

## Step 1 — Create the free Oracle VM

1. Sign up at <https://www.oracle.com/cloud/free/> (needs a card for identity check;
   Always Free resources are never charged).
2. **Create a Compute instance:**
   - Image: **Canonical Ubuntu 22.04**
   - Shape: **VM.Standard.A1.Flex** (Ampere ARM) — set **1 OCPU / 6 GB RAM**.
     This is Always Free eligible and has plenty of RAM for PyTorch inference.
     *(If you hit "out of capacity", retry in another Availability Domain or later —
     ARM capacity is in demand. The AMD `E2.1.Micro` free shape also works but only
     has 1 GB RAM, which is tight for the AI runs.)*
   - **Download the SSH private key** when prompted — you need it to log in.
3. After it boots, copy the instance's **Public IP address**.

---

## Step 2 — Point the subdomain at the VM (Namecheap)

1. Namecheap → **Domain List** → **Manage** on `shreyashrai.com` → **Advanced DNS**.
2. **Add New Record:**

   | Type     | Host           | Value                     | TTL       |
   |----------|----------------|---------------------------|-----------|
   | A Record | `lagrange-lock`| `<your Oracle VM public IP>` | Automatic |

3. Save. (DNS can take a few minutes to an hour to propagate.)

Verify from your own machine — it should print the VM's IP:

```bash
nslookup lagrange-lock.shreyashrai.com
```

---

## Step 3 — Open the firewall (the #1 Oracle gotcha — TWO layers)

HTTPS needs ports **80** and **443**. Oracle blocks them in *two* places:

**a) Cloud Security List** (in the Oracle web console):
Networking → your VCN → Security Lists → default → **Add Ingress Rules**:
- Source `0.0.0.0/0`, IP Protocol **TCP**, Destination port **80**
- Source `0.0.0.0/0`, IP Protocol **TCP**, Destination port **443**

**b) The VM's own iptables** (Ubuntu images ship with everything but SSH blocked).
SSH in (next step) and run:

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

---

## Step 4 — Install Docker, get the code, launch

SSH in using the key you downloaded:

```bash
ssh -i /path/to/your-key.key ubuntu@<your Oracle VM public IP>
```

Then:

```bash
# Docker + compose plugin
curl -fsSL https://get.docker.com | sudo sh

# Code (the deploy branch)
git clone -b deploy https://github.com/ItsMat78/Lagrange-Lock.git
cd Lagrange-Lock

# Build the image and start app + Caddy. Caddy auto-issues the TLS cert.
sudo DOMAIN=lagrange-lock.shreyashrai.com docker compose up -d --build
```

First build takes several minutes (PyTorch wheel). Then:

```bash
sudo docker compose ps              # both services "running"
sudo docker compose logs -f caddy   # watch the certificate get issued
```

Open **https://lagrange-lock.shreyashrai.com/realtime_viewer.html** 🎉

---

## Updating after you push changes

```bash
cd Lagrange-Lock
git pull
sudo DOMAIN=lagrange-lock.shreyashrai.com docker compose up -d --build
```

## Useful commands

```bash
sudo docker compose logs -f app   # server / AI inference logs
sudo docker compose restart app   # restart just the app
sudo docker compose down          # stop everything
```

---

## Notes / caveats

- If HTTPS won't issue, it's almost always the **firewall (Step 3)** or DNS not yet
  propagated. Confirm `nslookup` returns the right IP and port 80 is reachable.
- The server uses Python's single-threaded `http.server`, so it handles one request
  at a time — fine for a portfolio demo. AI runs are CPU-bound (20 sims/request), a
  few seconds each on this VM.
- Models live in `phase_3/models/` and are baked into the image at build time.

### Fully-free fallback (no cloud account)
If Oracle signup or ARM capacity is a blocker, you can instead run the server on your
own PC and expose it with a free **Cloudflare Tunnel** at the same subdomain — but
the site is only up while your PC is on, so it's weaker for a resume link. Ask and I
can write that variant up.
```
