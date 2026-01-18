# 🚀 GitHub Collaboration Workflow
**Project:** AI-Driven Station Keeping in Chaotic Gravitational Systems

This document outlines the standard operating procedure for our team to collaborate effectively, prevent code conflicts, and ensure all work is documented for weekly presentations.

---

## 🛠 Phase 1: One-Time Setup
*Complete this once at the start of the project.*

1.  **Repository Creation:**
    * One person creates the repo on GitHub.
    * Go to **Settings > Collaborators > Add people** and invite the teammate.
2.  **Clone the Repo:**
    * Both team members run this in their terminal:
    ```bash
    git clone [https://github.com/ItsMat78/Lagrange-Lock.git](https://github.com/ItsMat78/Lagrange-Lock.git)
    cd Lagrange-Lock
    ```

---

## 🔄 Phase 2: The Daily Workflow (The "Golden Rule")
**RULE:** Never push directly to the `main` branch. Always work on a "feature branch."

### Step 1: Start Fresh
Before you start coding for the day, update your local machine with your teammate's latest work.
```bash
git checkout main
git pull origin main

```

### Step 2: Create a Branch

Name your branch based on the task (e.g., `physics-engine`, `noise-sensor`, `readme-update`).

```bash
git checkout -b feature/name-of-task

```

### Step 3: Code & Save

Work on your files. When ready to save a checkpoint:

```bash
git add .
git commit -m "Brief description of what you added"

```

### Step 4: Upload Your Branch

Push your specific branch to GitHub (not `main`).

```bash
git push origin feature/name-of-task

```

---

## 🔀 Phase 3: Merging & Review

*This is how we combine our work and create documentation for the professor.*

1. **Open a Pull Request (PR):**
* Go to the GitHub repository page.
* Click the green **"Compare & pull request"** button.
* **Title:** Clear summary (e.g., "Added Gravity Simulation Logic").
* **Description:** Bullet points explaining *what* changed. (This is key for our weekly updates!).


2. **Review & Merge:**
* The *other* teammate reviews the code.
* If it looks good, click **Merge pull request**.
* Delete the branch after merging.



---

## 📋 Phase 4: Project Management (Kanban)

*Use this for weekly updates with Professor.*

1. Go to the **Projects** tab in the repo.
2. Use the Board to track tasks:
* **To Do:** Future tasks (e.g., "Design RL Reward Function").
* **In Progress:** What we are working on *now*.
* **Done:** Completed tasks (Show this list during presentations).



---

## 🆘 Troubleshooting:

If your contributions aren't showing up on your profile, your local Git email might not match your GitHub account.

**Check current email:**

```bash
git config user.email

```

**Fix it:**

```bash
git config --global user.email "your_real_github_email@example.com"
git config --global user.name "Your Real Name"

```

```

```