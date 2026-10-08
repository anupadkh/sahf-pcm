# First-time server toDos

Target: Ubuntu 24.04, Bash, Python 3.12, Nginx and Supervisor. Default deployment directory: `/opt/pcm`. Replace `pcm.example.com` with your domain everywhere. Production uses static Angular files, not `ng serve`. Node 22.12+ is needed on the build machine; production needs only Python because GitHub builds Angular.

## 1. Machine, domain and packages

- Point the domain's DNS A record to the server. Add an AAAA record only if IPv6 works.
- Keep an SSH session open while configuring the firewall; allow your SSH port first.
- Install packages:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx supervisor curl ca-certificates openssh-server util-linux
sudo ufw allow OpenSSH             # Adjust if SSH uses another port.
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo systemctl enable --now nginx supervisor
```

Do not expose port 8000 or 4200 publicly. Backend binds to loopback. Finish TLS setup before entering production credentials.

## 2. Service/deployment account and directories

```bash
sudo adduser --disabled-password --gecos '' pcm
sudo install -d -o pcm -g pcm -m 755 /opt/pcm /opt/pcm/releases /opt/pcm/uploads /opt/pcm/bin
sudo install -d -o pcm -g pcm -m 750 /opt/pcm/shared /opt/pcm/shared/backups
sudo install -d -o pcm -g pcm -m 750 /var/log/pcm
```

Copy this project's `backend`, `frontend` and `server` folders to `/opt/pcm/releases/initial`. The initial frontend must include `frontend/dist/pcm/browser/index.html`. Build on your workstation/CI with `npm ci && npm run build:production`, or use `server/scripts/build-frontend.sh` on a Linux build machine with supported Node installed. Do not copy local `.venv`, `node_modules`, test databases or production secrets.

```bash
sudo chown -R pcm:pcm /opt/pcm/releases/initial
sudo chmod -R a+rX /opt/pcm/releases/initial
sudo -u pcm python3 -m venv /opt/pcm/releases/initial/backend/.venv
sudo -u pcm /opt/pcm/releases/initial/backend/.venv/bin/python -m pip install -r /opt/pcm/releases/initial/backend/requirements.txt
sudo -u pcm ln -s /opt/pcm/releases/initial /opt/pcm/current
sudo install -o root -g pcm -m 640 /opt/pcm/current/server/conf/pcm.env.example /opt/pcm/shared/pcm.env
sudoedit /opt/pcm/shared/pcm.env
sudo install -o root -g root -m 755 /opt/pcm/current/server/scripts/deploy.sh /opt/pcm/bin/deploy.sh
```

Keep `PCM_SEED_DEMO=false`; this prevents sample users with the development password. Set `PCM_ORIGINS=https://YOUR_DOMAIN`. Keep `PCM_DB=/opt/pcm/shared/pcm.sqlite3`; releases must never own the live database. `pcm.env` uses shell syntax and is read by startup/deployment scripts. An existing production database can be copied into this shared path before starting; keep its ownership `pcm:pcm` and permissions `600`. Never copy a demo database into production.

Create the first admin interactively (the password is not placed in shell history):

```bash
sudo -u pcm /bin/bash -c 'set -a; source /opt/pcm/shared/pcm.env; set +a; /opt/pcm/current/backend/.venv/bin/python /opt/pcm/current/server/scripts/create-admin.py'
sudo chmod 600 /opt/pcm/shared/pcm.sqlite3
```

## 3. Supervisor and Nginx

```bash
sudo install -m 644 /opt/pcm/current/server/conf/supervisor.conf /etc/supervisor/conf.d/pcm.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status pcm-backend
curl --fail http://127.0.0.1:8000/api/health
sudo install -m 644 /opt/pcm/current/server/conf/nginx.conf /etc/nginx/sites-available/pcm
sudoedit /etc/nginx/sites-available/pcm  # Replace pcm.example.com.
sudo ln -s /etc/nginx/sites-available/pcm /etc/nginx/sites-enabled/pcm
sudo nginx -t
sudo systemctl reload nginx
```

If this host is dedicated to PCM, remove the default site's enabled symlink after confirming it is not needed. Do not remove other sites. Verify the homepage, `/login`, `/administrator/records`, `/administrator/users`, `/administrator/audit` and `/api/health` through Nginx; private pages must require sign-in. Excel uploads allow 10 MB; Nginx allows 11 MB to accommodate multipart overhead.

Install HTTPS after DNS resolves:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN
sudo certbot renew --dry-run
```

Certbot updates Nginx to use certificates and redirects HTTP to HTTPS. Verify the domain over HTTPS and renewal scheduling. GitHub deployment does not overwrite system Nginx/Supervisor configs or server environment files; apply future config edits deliberately with `nginx -t` / `supervisorctl reread`.

## 4. GitHub Actions → server

The workflow is `.github/workflows/deploy.yml`. It recognizes either `backend/frontend/server` at repo root or beneath `implementation/`. The workflow must be at the GitHub repository root's `.github/workflows/`, not just under `implementation/` if that is a subfolder.

1. Generate a dedicated deployment SSH key on an administrator machine. Store its private key only in GitHub secrets, and install the public key in `/home/pcm/.ssh/authorized_keys` (directory mode 700, file mode 600, owner pcm). Add `restrict` before the public key to disable forwarding and PTY; remote deployment commands still need to run.
2. Obtain the server's SSH host public key from the server console or another trusted channel and verify its fingerprint. Create the `SSH_KNOWN_HOSTS` entry for your hostname, using `[hostname]:port` for non-default ports. Do not automatically trust an unverified `ssh-keyscan` result.
3. Use `sudo visudo -f /etc/sudoers.d/pcm-deploy` to add exactly:

```sudoers
pcm ALL=(root) NOPASSWD: /usr/bin/supervisorctl restart pcm-backend
```

4. Create a GitHub environment named `production`. Set deployment branch restriction to `main`; optional required reviewers depend on your GitHub plan. Add these secrets:

| Secret | Value |
| --- | --- |
| SSH_HOST | Server hostname or IPv4 address |
| SSH_USER | pcm |
| SSH_PORT | SSH port; defaults to 22 |
| SSH_PRIVATE_KEY | Deployment private key, including header/footer |
| SSH_KNOWN_HOSTS | Verified SSH host-key entry |

5. Push to `main`, or manually run the workflow on `main`. Pull requests run tests/build only. The verify job installs backend dependencies, runs tests, checks Bash syntax and builds Angular. The deploy job uploads a release over SSH and runs the previously installed `/opt/pcm/bin/deploy.sh`.

The deploy script locks deployments, installs a new release-specific virtualenv, backs up SQLite with the SQLite backup API, atomically switches `/opt/pcm/current`, restarts FastAPI and checks `/api/health`. Failed health checks roll the code back; database changes are not automatically reverted. Startup migrations currently add fields/tables. Future destructive migrations require a separate migration/restore plan. Expect a short restart interval, not zero downtime. Keep previous releases and backups; schedule retention separately after successful deployments. Server needs outbound access to the Python package index during dependency installation.

## 5. Operations checklist

- Sign in with your new admin, create real users, and test record creation, XLSX issue handling, review, publication, deletion and public visibility.
- Preserve `/opt/pcm/shared/pcm.sqlite3`, `pcm.env`, backups and SSH keys outside release archives. Schedule encrypted/off-server database backups and rehearse restoration.
- Logs: `/var/log/pcm/backend.log`, `/var/log/nginx/pcm-access.log`, `/var/log/nginx/pcm-error.log`. Supervisor rotates backend logs; verify Nginx logrotate.
- For rollback: point `/opt/pcm/current` to a previously verified release, then `sudo supervisorctl restart pcm-backend`. Do not restore a database backup without first stopping writes and reviewing which records would be lost.
- Keep OS security updates and certificate renewal enabled; monitor free disk space and backend health.
- The backend's SQLite configuration is intended for a single host/process. Use PostgreSQL and deliberate migrations before scaling across hosts.

## Local Linux development

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend && npm ci && cd ..
bash server/scripts/run-backend.sh   # Terminal 1: http://127.0.0.1:8000
bash server/scripts/run-frontend.sh  # Terminal 2: http://127.0.0.1:4200, proxies /api to 8000
```

These scripts are Bash/Linux scripts. The production Supervisor configuration runs the backend only; Nginx serves the frontend. The WMO logo is loaded from wmo.int, so browsers need access to that host.

## Configuration references

- [Nginx core directives](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [Supervisor program configuration](https://supervisord.org/configuration.html)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
