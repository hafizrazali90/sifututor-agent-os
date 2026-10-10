"""Create a lane conf (mode 600) with a generated password, or reuse it; render a SQL template to stdout.
Usage: make_conf.py <conf-path> <PREFIX> <template> KEY=VALUE...  Never prints the password except into the rendered SQL on stdout (piped to the server)."""
import os, sys, secrets, string, re
conf, prefix, tmpl, *kv = sys.argv[1:]
vals = {}
if os.path.exists(conf):
    for line in open(conf):
        m = re.match(r'^([A-Z0-9_]+)=(.*)$', line.strip())
        if m: vals[m.group(1)] = m.group(2).strip('"')
pw_key = f"{prefix}_PASSWORD"
if pw_key not in vals:
    alphabet = string.ascii_letters + string.digits
    vals[pw_key] = "Aa1" + "".join(secrets.choice(alphabet) for _ in range(37))
for item in kv:
    k, v = item.split("=", 1); vals[f"{prefix}_{k}"] = v
os.makedirs(os.path.dirname(conf), exist_ok=True)
fd = os.open(conf, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    f.write("# Agent read-only lane. Never print or commit this file.\n")
    for k in sorted(vals): f.write(f'{k}="{vals[k]}"\n')
os.chmod(conf, 0o600)
sys.stdout.write(open(tmpl).read().replace("__PASSWORD__", vals[pw_key]))
