# Deployment Guide (VPS + Automated CI/CD)

This guide explains how to deploy the **Commodity Risk Sentinel Agent** to a Virtual Private Server (VPS) and set up automatic deployment via GitHub Actions.

## 1. Prerequisites

- A VPS (e.g., AWS EC2, DigitalOcean Droplet, Linode, Vultr).
- SSH access to your server.
- Python 3.8 or higher installed on the server.
- A GitHub repository for this project.

## 2. Server Setup (First Time Only)

1.  **SSH into your server**:
    ```bash
    ssh user@your-vps-ip
    ```

2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/Commodity_Risk_Sentinel_Agent.git
    cd Commodity_Risk_Sentinel_Agent
    ```

3.  **Setup Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Configure `.env`**:
    ```bash
    cp credentials.template .env
    nano .env
    # Fill in your API Keys
    ```

5.  **Verify Setup**:
    ```bash
    venv/bin/python -m sentinel.main
    ```

6.  **Setup Cron (Scheduler)**:
    - Run `crontab -e` and add:
      ```bash
      0 * * * * cd /home/user/Commodity_Risk_Sentinel_Agent && /home/user/Commodity_Risk_Sentinel_Agent/venv/bin/python -m sentinel.main >> sentinel.log 2>&1
      ```
    - *Replace `/home/user/...` with your actual path.*

---

## 3. Automated Deployment (CI/CD)

We use **GitHub Actions** to automatically update the server whenever you push code to `main`.

### A. Configure GitHub Secrets

For GitHub to access your server, you need to provide credentials securely.

1.  Go to your GitHub Repository -> **Settings**.
2.  On the left sidebar, click **Secrets and variables** -> **Actions**.
3.  Click **New repository secret** and add the following 3 secrets:

| Name | Value |
| :--- | :--- |
| `HOST` | The Public IP address of your VPS (e.g., `123.45.67.89`). |
| `USERNAME` | The SSH username (e.g., `root` or `ubuntu`). |
| `SSH_KEY` | Your **Private SSH Key**. <br> 1. On your local machine, run `cat ~/.ssh/id_rsa` (or your key file). <br> 2. Copy the **entire** content (start with `-----BEGIN...` end with `...END-----`). <br> 3. Paste it here. |

### B. Trigger Deployment

1.  Make a change to your code on your local machine.
2.  Commit and push:
    ```bash
    git add .
    git commit -m "Update agent logic"
    git push origin main
    ```
3.  Go to the **Actions** tab on GitHub to watch the deployment status.
4.  Once green, your server is updated!
