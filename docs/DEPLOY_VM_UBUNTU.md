# Deploy `jd-extraction` To An Ubuntu VM

This guide assumes:
- Ubuntu 22.04 or 24.04
- a fresh VM
- repo path: `/opt/jd-extraction`
- app user: `ubuntu`
- backend bound to `127.0.0.1:8001`
- Streamlit UI bound to `127.0.0.1:8501`
- Nginx exposed on port `80`

## 1. SSH into the VM

```bash
ssh ubuntu@YOUR_VM_PUBLIC_IP
```

## 2. Install OS packages

```bash
sudo apt update
sudo apt install -y git python3.12 python3.12-venv python3-pip nginx
```

If `python3.12` is not available in your image, verify the installed Python first:

```bash
python3 --version
```

If your VM only has `python3.10` or `python3.11`, either install 3.12 from your base image’s supported source or update the service paths and venv creation command accordingly.

## 3. Clone the repo

```bash
cd /opt
sudo git clone https://github.com/tvarahRepo/jd-extraction.git
sudo chown -R ubuntu:ubuntu /opt/jd-extraction
cd /opt/jd-extraction
```

## 4. Create the Python virtual environment

```bash
cd /opt/jd-extraction
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Create the environment file

```bash
cd /opt/jd-extraction
cp .env.example .env
nano .env
```

Set these values:

```env
OPENROUTER_API_KEY=YOUR_REAL_OPENROUTER_KEY
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MISTRAL_API_KEY=YOUR_REAL_MISTRAL_KEY
TEMPERATURE=0
MAX_RETRIES=1
```

Save and exit.

## 6. Smoke test manually before services

Terminal 1:

```bash
cd /opt/jd-extraction
source .venv/bin/activate
./run_backend.sh
```

You should see Uvicorn start on `127.0.0.1:8001`.

Open a second SSH session.

Terminal 2:

```bash
cd /opt/jd-extraction
source .venv/bin/activate
./run_ui.sh
```

You should see Streamlit start on `127.0.0.1:8501`.

## 7. Verify both local endpoints

From the VM:

```bash
curl http://127.0.0.1:8001/health
curl -I http://127.0.0.1:8501
```

Expected:
- backend returns `{"status":"ok"}`
- Streamlit returns `HTTP/1.1 200 OK`

Stop both manual processes with `Ctrl+C` after validation.

## 8. Install the systemd services

Copy the service files:

```bash
sudo cp /opt/jd-extraction/deploy/systemd/jd-backend.service /etc/systemd/system/jd-backend.service
sudo cp /opt/jd-extraction/deploy/systemd/jd-ui.service /etc/systemd/system/jd-ui.service
```

Reload systemd and enable the services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable jd-backend
sudo systemctl enable jd-ui
sudo systemctl start jd-backend
sudo systemctl start jd-ui
```

Check status:

```bash
sudo systemctl status jd-backend --no-pager
sudo systemctl status jd-ui --no-pager
```

If there is a failure, inspect logs:

```bash
sudo journalctl -u jd-backend -n 100 --no-pager
sudo journalctl -u jd-ui -n 100 --no-pager
```

## 9. Configure Nginx

Copy the Nginx file:

```bash
sudo cp /opt/jd-extraction/deploy/nginx/jd-extraction.conf /etc/nginx/sites-available/jd-extraction
```

Edit the server name:

```bash
sudo nano /etc/nginx/sites-available/jd-extraction
```

Replace:

```nginx
server_name YOUR_DOMAIN_OR_VM_IP;
```

With either:
- your DNS name, for example `jd.example.com`
- or the VM public IP if you do not have DNS yet

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/jd-extraction /etc/nginx/sites-enabled/jd-extraction
sudo nginx -t
sudo systemctl restart nginx
```

## 10. Open firewall ports

If UFW is enabled:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

If your cloud provider also has security groups or network ACLs, allow:
- inbound `80`
- inbound `443` if you will add TLS

You do not need to expose `8001` or `8501` publicly because Nginx proxies locally to them.

## 11. Validate from your browser

Open:

```text
http://YOUR_DOMAIN_OR_VM_IP
```

You should see the JD Extraction Studio UI.

Upload a JD PDF or DOCX and submit it.

## 12. Updating the deployment after a new push

On the VM:

```bash
cd /opt/jd-extraction
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart jd-backend
sudo systemctl restart jd-ui
```

## 13. Optional TLS with Certbot

If you have a real domain:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN
```

Then test auto-renewal:

```bash
sudo certbot renew --dry-run
```

## 14. Most common failure points

- `500 Internal Server Error` on upload:
  Usually missing or invalid `OPENROUTER_API_KEY` or `MISTRAL_API_KEY`.
- UI loads but parsing hangs:
  Usually outbound access from the VM to Mistral/OpenRouter is blocked.
- `ModuleNotFoundError`:
  Re-run `pip install -r requirements.txt` inside `/opt/jd-extraction/.venv`.
- Nginx shows `502 Bad Gateway`:
  Check `jd-backend` and `jd-ui` service status first.

