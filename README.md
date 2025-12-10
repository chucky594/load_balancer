# Web Service Load Balancing

## Overview
This project demonstrates a simple HTTP load-balancing setup using HAProxy (on Ubuntu) distributing traffic between two web servers:
- Ubuntu 24.04 running Nginx + Flask (local backend)
- Rocky Linux running Apache (httpd) + Flask

HAProxy performs health checks and balances traffic on port **8000** (HTTP). TLS/SSL termination is *optional* and not covered in this dev README.

---

## Prerequisites
You need:
- SSH access to both servers (Ubuntu and Rocky)
- sudo privileges on both servers
- Local git, Python 3.11+, pip
- Packages: `nginx`, `httpd` (on Rocky), `haproxy`, `python3-venv`, `gunicorn`, `flask`

Install (Ubuntu):
```bash
sudo apt update
sudo apt install -y nginx haproxy python3-venv python3-pip
```

Install (Rocky):
```bash
sudo dnf install -y nginx httpd python3-venv python3-pip  # if using nginx on Rocky; adjust as needed
sudo dnf install -y httpd
```

---

## Clone & Install
```bash
git clone https://github.com/chucky594/load_balancer.git
cd load_balancer

# create python venv and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration notes

**Health endpoint:** The Flask app exposes `/health`. Ensure HAProxy uses the same endpoint:
```cfg
# in backend web_servers (HAProxy)
http-check send meth GET uri /health ver HTTP/1.1 hdr Host 127.0.0.1
http-check expect status 200
```

**HAProxy server lines:** If HAProxy runs on the **same Ubuntu host** as Nginx, refer to the Ubuntu backend as `127.0.0.1:80`. If HAProxy is remote, use the Ubuntu host IP.

---

## HAProxy example config (place in /etc/haproxy/haproxy.cfg)
```cfg
global
    log /dev/log local0 notice
    daemon
    maxconn 2000

defaults
    log     global
    mode    http
    option  httplog
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend http_front
    bind *:8000
    default_backend web_servers

backend web_servers
    mode http
    balance roundrobin
    option forwardfor
    http-check send meth GET uri /health ver HTTP/1.1 hdr Host 127.0.0.1
    http-check expect status 200

    server ubuntu_nginx 127.0.0.1:80 check inter 2000 rise 2 fall 3
    server rocky_apache 192.168.1.101:80 check inter 2000 rise 2 fall 3
```

Validate and start HAProxy:
```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg       # config check
sudo systemctl enable --now haproxy
sudo journalctl -u haproxy -f                     # follow logs
```

---

## Start/verify web services
Ubuntu (Nginx):
```bash
sudo systemctl enable --now nginx
sudo systemctl status nginx
```

Rocky (httpd):
```bash
sudo systemctl enable --now httpd
sudo systemctl status httpd
```

Test endpoints (on each server use localhost; remote use server IP):
```bash
# on Ubuntu:
curl -sS http://127.0.0.1/        # nginx + flask app
curl -sS http://127.0.0.1/health # health check

# on Rocky:
curl -sS http://127.0.0.1/
curl -sS http://127.0.0.1/health
```

HAProxy test (from any client):
```bash
curl -sS http://192.168.1.166:8000/    # should alternate between backends
```

To test failover:
```bash
# stop Rocky backend
sudo systemctl stop httpd
# HAProxy should mark rocky_apache DOWN and serve ubuntu only
```

---

## Firewall (Dev vs Production)
**Development (temporary)**:
```bash
# Ubuntu (ufw)
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp

# Rocky (firewalld)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**Do not disable firewalls permanently in production.** Instead open only required ports and restrict access.

---

## Troubleshooting / Common issues
- **HAProxy marks backend DOWN with 503** → health endpoint mismatch. Ensure backend responds 200 at `/health`. Use `curl` on backend to confirm.
- **`haproxy -c` error about httpchk** → update to `http-check send` (HAProxy 3.x)
- **Permission errors installing pip packages** → ensure venv ownership: `sudo chown -R $(whoami):$(whoami) /opt/Flask_app` or recreate venv as your user.
- **Systemd service failing with Address already in use** → check `ss -ltnp | grep :5000` and kill leftover gunicorns; ensure service binds to free port.
- **Nginx config test fails: duplicate default server** → remove extra `default_server` or disable default site in `/etc/nginx/sites-enabled/`.
- **Do not add private SSH keys to GitHub** — only upload your public key (`~/.ssh/id_ed25519.pub`) to your GitHub account.

---

## Summary
- Keep health endpoints consistent (`/health` recommended).  
- Use `haproxy -c` + `journalctl` to debug HAProxy.  
- Configure firewall rules instead of disabling firewalls in production.  
- Do not publish private keys.  

   


