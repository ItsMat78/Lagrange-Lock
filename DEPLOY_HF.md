# Deploying Lagrange-Lock free on Hugging Face Spaces

This hosts the Phase 3 server (physics + PPO inference + Three.js frontend) on a
**free Hugging Face Space** — no credit card, no VM to manage, automatic HTTPS,
2 vCPU / 16 GB RAM. Then a **Namecheap URL Redirect** makes
`lagrange-lock.shreyashrai.com` point at it.

HF reads its build config from the YAML header already added to `README.md`
(`sdk: docker`, `app_port: 8081`). The same `Dockerfile` is used as-is.

---

## Step 1 — Create the Space

1. Sign up at <https://huggingface.co/join> (free, no card).
2. Create a token: **Settings → Access Tokens → New token**, role **Write**. Copy it.
3. New Space: <https://huggingface.co/new-space>
   - **Owner:** your username
   - **Space name:** `lagrange-lock`
   - **SDK:** **Docker** → **Blank**
   - **Hardware:** **CPU basic (free)**
   - Visibility: **Public**
   - Click **Create Space**.

Your Space URL will be **`https://<your-hf-username>-lagrange-lock.hf.space`**
(note the format: `username` + `-` + `space-name`).

---

## Step 2 — Push the code to the Space

The Space is its own git repo. From your local clone, on the `deploy` branch:

```bash
git checkout deploy

# Add the Space as a remote (use YOUR username)
git remote add hf https://huggingface.co/spaces/<your-hf-username>/lagrange-lock

# Push the deploy branch to the Space's main branch.
# When prompted: username = your HF username, password = the WRITE token from Step 1.
git push hf deploy:main
```

HF immediately starts building the Docker image. Watch progress on the Space page
(the **Logs** / **App** tabs). First build takes a few minutes (PyTorch wheel).

When it shows **Running**, open:
**`https://<your-hf-username>-lagrange-lock.hf.space/realtime_viewer.html`** 🎉

> Note: the app loads at the `/realtime_viewer.html` path. The bare Space URL will
> show a directory listing — see "Optional polish" below to make `/` load the viewer.

---

## Step 3 — Point the subdomain at it (Namecheap redirect)

1. Namecheap → **Domain List** → **Manage** on `shreyashrai.com` → **Advanced DNS**.
2. **Add New Record** → choose **URL Redirect Record**:

   | Type               | Host           | Value                                                     |
   |--------------------|----------------|----------------------------------------------------------|
   | URL Redirect Record| `lagrange-lock`| `https://<your-hf-username>-lagrange-lock.hf.space/realtime_viewer.html` |

3. Set redirect type to **Permanent (301)**, **Unmasked**. Save.

Now `https://lagrange-lock.shreyashrai.com` forwards straight to the live app.
(The browser's address bar will end on the `hf.space` URL — that's expected with an
unmasked redirect. "Masked" keeps your domain visible but uses an iframe and is worse
for HTTPS/sharing, so unmasked is recommended.)

---

## Updating after you push changes

```bash
git push hf deploy:main      # HF rebuilds automatically
```

## Notes / caveats

- **Free Spaces sleep after ~48h of inactivity** and cold-start on the next visit
  (a few seconds to wake). Fine for a resume link; just expect an occasional spin-up.
- AI runs are CPU-bound (20 sims/request) — a few seconds each on the free CPU.
- The `Dockerfile`, `docker-compose.yml`, and `Caddyfile` also support a self-hosted
  VPS (see `DEPLOY.md`). HF only uses the `Dockerfile`; the rest is ignored there.
- Want your subdomain to stay in the address bar (no redirect)? That needs HF's custom
  domain feature, which is a paid PRO plan — or the Oracle VPS route in `DEPLOY.md`.

### Optional polish — make `/` load the viewer
Right now the app lives at `/realtime_viewer.html`. If you'd like the bare URL to load
it directly, rename/copy `phase_3/realtime_viewer.html` to `phase_3/index.html` (the
server serves `index.html` automatically for `/`). Ask and I can do this cleanly.
```
