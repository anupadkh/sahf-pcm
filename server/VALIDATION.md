# Deployment file validation

- Backend: 22 tests passed.
- Angular: production build completed with hashed assets.
- Bash startup/build/deploy scripts: syntax checked with `bash -n`.
- Bootstrap Python script: compiled successfully.
- GitHub workflow: YAML parsed; verify/deploy jobs and production environment verified.
- Supervisor: configuration parsed with Python ConfigParser.
- Angular development proxy: JSON parsed.

This Windows workspace has no Nginx/Supervisor Linux runtime. Run `sudo nginx -t`, `sudo supervisorctl reread`, and the health checks in README.md on the server before enabling deployment. No remote machine or GitHub account was changed.
