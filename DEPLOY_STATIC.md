# Deploying Lagrange-Lock to `lagrange-lock.shreyashrai.com` (free, static, always-on)

The viewer in [`docs/`](docs/) runs the **entire demo in the browser** — the CR3BP
physics, the PPO policy, and the best-of-20 rollout are all ported to JavaScript
([`docs/index.html`](docs/index.html)) and read the trained weights from
[`docs/policy.json`](docs/policy.json). **No server, no Python, no card.**

That means it can be hosted as plain static files on **GitHub Pages**, with your
real subdomain in the address bar (a proper `CNAME`, not a redirect), always on,
no cold starts.

> The policy weights were exported with [`phase_3/export_policy.py`](phase_3/export_policy.py)
> and verified to match Stable-Baselines3's `predict()` to ~1e-7. To regenerate
> after retraining: `python phase_3/export_policy.py`.

---

## Step 1 — Enable GitHub Pages from `docs/`

1. Push the `deploy` branch (already done) so `docs/` is on GitHub.
2. Repo → **Settings → Pages**.
3. **Build and deployment → Source: Deploy from a branch.**
4. Branch: **`deploy`**, folder: **`/docs`**. Save.

GitHub builds the site. The `docs/CNAME` file already contains
`lagrange-lock.shreyashrai.com`, so Pages will expect that domain.

> Keeping Pages on the `deploy` branch leaves `main` untouched. If you'd rather
> serve from `main`, merge `deploy` into `main` first and pick `main /docs`.

---

## Step 2 — Point the subdomain at GitHub Pages (Namecheap)

1. Namecheap → **Domain List** → **Manage** on `shreyashrai.com` → **Advanced DNS**.
2. **Add New Record:**

   | Type        | Host           | Value                 | TTL       |
   |-------------|----------------|-----------------------|-----------|
   | CNAME Record| `lagrange-lock`| `itsmat78.github.io.` | Automatic |

   (Use **your** GitHub username if it isn't `itsmat78`. The trailing dot is fine.)
3. Save. DNS can take a few minutes to an hour.

Back in **Settings → Pages**, once it verifies the domain, tick
**Enforce HTTPS** (GitHub issues the certificate automatically — may take a few
minutes to appear).

Open **https://lagrange-lock.shreyashrai.com** 🎉

---

## Updating

Edit files in `docs/`, commit, and `git push origin deploy`. Pages redeploys
automatically in ~1 minute.

---

## How it works (for the README / interview questions)

- `docs/index.html` is the Phase 3 viewer with the server calls removed. The
  `/simulate`, `/simulate_ai`, and `/models` endpoints are replaced by in-browser
  functions: `simulatePhysics`, `rolloutBestOf`, and `loadPolicies`.
- `cr3bpDerivs` / `rk4Step` mirror `phase_3/fast_dynamics.py`.
- `envStep` mirrors `SatelliteEnv.step` (thrust, fuel, reward, termination).
- `policyMean` / `policySample` implement the SB3 `MlpPolicy` forward pass
  (two `tanh` layers + linear action head) and Gaussian sampling via `log_std`.
- `policy.json` holds the exported weights for three checkpoints (0.5M / 2M / 5M)
  so the dropdown demonstrates training convergence.

## Caveats

- The rollout is CPU-bound JavaScript on the main thread; a 20×5000-step run takes
  ~1 second and briefly shows the loading overlay. Could move to a Web Worker later
  if you want the UI fully responsive during compute.
- Three.js loads from the unpkg CDN (already in the import map) — needs internet,
  which any visitor has anyway.
- The Docker / Oracle / HF guides (`DEPLOY.md`, `DEPLOY_HF.md`) remain as
  alternative server-based options, but this static path is the recommended one.
