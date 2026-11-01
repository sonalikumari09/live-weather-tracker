#!/usr/bin/env bash
# ==============================================================================
# owp-repin.sh — re-embed the LIVE local builds into owp-doctor.sh
#
# Picks up whatever is currently installed on this machine:
#   ~/.local/bin/opencode-proxy
#   ~/.config/opencode/plugins/privacy-shield.js
# rewrites the two embedded payloads + hash gates inside owp-doctor.sh,
# verifies the round-trip byte-for-byte, and optionally republishes the gist
# in place (same URL, new revision).
#
#   ./owp-repin.sh                  repin locally, verify, no network
#   ./owp-repin.sh --gist           repin + update gist + print pinned URL
#   ./owp-repin.sh --proxy P --plugin Q --doc D
#   ./owp-repin.sh --force          allow a legacy build through the guards
# ==============================================================================
set -euo pipefail

DOC="${DOC:-$HOME/owp-doctor.sh}"
PROXY="${PROXY:-$HOME/.local/bin/opencode-proxy}"
PLUGIN="${PLUGIN:-$HOME/.config/opencode/plugins/privacy-shield.js}"
GIST="${GIST:-ccffdf28e4060064be9feb2a99c491b9}"
DO_GIST=0
FORCE=0

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
say() { printf '%s\n' "$*"; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --doc)    DOC="$2"; shift 2 ;;
        --proxy)  PROXY="$2"; shift 2 ;;
        --plugin) PLUGIN="$2"; shift 2 ;;
        --gist)   DO_GIST=1
                  if [[ ${2:-} == gist_* || ${2:-} == [0-9a-f]* ]]; then GIST="$2"; shift; fi
                  shift ;;
        --no-gist) DO_GIST=0; shift ;;
        --force)  FORCE=1; shift ;;
        --help|-h) sed -n '3,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) die "unknown flag: $1" ;;
    esac
done

hash_file() {
    if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
    else shasum -a 256 "$1" | awk '{print $1}'; fi
}

[[ -f "$DOC" ]]    || die "doctor script not found: $DOC"
[[ -f "$PROXY" ]]  || die "proxy not found: $PROXY"
[[ -f "$PLUGIN" ]] || die "plugin not found: $PLUGIN"
[[ -s "$PROXY" ]]  || die "proxy is empty: $PROXY"
[[ -s "$PLUGIN" ]] || die "plugin is empty: $PLUGIN"

grep -q '^PROXY_B64=' "$DOC"  || die "$DOC has no PROXY_B64 block"
grep -q '^PLUGIN_B64=' "$DOC" || die "$DOC has no PLUGIN_B64 block"

# Guard rails: these are the two files that broke the friend's box.
if grep -q 'PLUGIN_EOF' "$PROXY" && [[ "$FORCE" -ne 1 ]]; then
    die "$PROXY still embeds the old plugin generator (legacy 36KB build). Point --proxy at ~/.local/bin/opencode-proxy, or pass --force."
fi
if grep -q 'MAX_RETRIES = 12' "$PLUGIN" && [[ "$FORCE" -ne 1 ]]; then
    die "$PLUGIN is the legacy 12-resume build. Pass --force only if that is deliberate."
fi

HASH_PROXY_NEW="$(hash_file "$PROXY")"
HASH_PLUGIN_NEW="$(hash_file "$PLUGIN")"
SIZE_PROXY="$(wc -c < "$PROXY" | tr -d ' ')"
SIZE_PLUGIN="$(wc -c < "$PLUGIN" | tr -d ' ')"

say "source proxy  $PROXY  ($SIZE_PROXY bytes)  ${HASH_PROXY_NEW:0:16}…"
say "source plugin $PLUGIN ($SIZE_PLUGIN bytes)  ${HASH_PLUGIN_NEW:0:16}…"

TMP="$(mktemp "${TMPDIR:-/tmp}/owp-repin.XXXXXX")"
trap 'rm -f "$TMP"' EXIT

# Short-circuit when the embedded payloads already equal the live files.
if python3 - "$DOC" "$PROXY" "$PLUGIN" <<'PY'
import base64, gzip, re, sys
doc, proxy, plugin = sys.argv[1:4]
src = open(doc, encoding="utf-8").read()
def extract(name):
    m = re.search(name + r"='\n(.*?)\n'", src, re.S)
    return gzip.decompress(base64.b64decode(m.group(1))) if m else None
ok = extract("PROXY_B64") == open(proxy, "rb").read() and \
     extract("PLUGIN_B64") == open(plugin, "rb").read()
sys.exit(0 if ok else 3)
PY
then
    say "already pinned to the live files — no rewrite needed"
    say ""
    say "doctor sha256  $(hash_file "$DOC")"
    if [[ "$DO_GIST" -eq 1 ]]; then
        say ""
        say "gist           https://gist.github.com/pritkr/$GIST"
    fi
    exit 0
fi

python3 - "$DOC" "$PROXY" "$PLUGIN" "$HASH_PROXY_NEW" "$HASH_PLUGIN_NEW" "$TMP" <<'PY'
import base64, gzip, io, re, sys

doc_path, proxy_path, plugin_path, h_proxy, h_plugin, out_path = sys.argv[1:7]
src = open(doc_path, encoding="utf-8").read()

def payload(path):
    raw = open(path, "rb").read()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(raw)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return "\n".join(b64[i:i + 100] for i in range(0, len(b64), 100)), raw

proxy_b64, proxy_raw = payload(proxy_path)
plugin_b64, plugin_raw = payload(plugin_path)

for name, blob in (("PROXY_B64", proxy_b64), ("PLUGIN_B64", plugin_b64)):
    pat = re.compile(name + r"='\n.*?\n'", re.S)
    if not pat.search(src):
        sys.exit("missing block: " + name)
    src = pat.sub(lambda m: name + "='\n" + blob + "\n'", src, count=1)

src = re.sub(r"^HASH_PROXY=[0-9a-f]+$", "HASH_PROXY=" + h_proxy, src, count=1, flags=re.M)
src = re.sub(r"^HASH_PLUGIN=[0-9a-f]+$", "HASH_PLUGIN=" + h_plugin, src, count=1, flags=re.M)

open(out_path, "w", encoding="utf-8").write(src)
print("rewrote payloads: proxy %d bytes, plugin %d bytes" % (len(proxy_raw), len(plugin_raw)))
PY

bash -n "$TMP" || die "rewritten script failed bash -n"

# Round-trip: extract from the NEW doc and compare to the live files byte-for-byte.
python3 - "$TMP" "$PROXY" "$PLUGIN" <<'PY'
import base64, gzip, re, sys

doc, proxy, plugin = sys.argv[1:4]
src = open(doc, encoding="utf-8").read()

def extract(name):
    m = re.search(name + r"='\n(.*?)\n'", src, re.S)
    if not m:
        sys.exit("missing " + name)
    return gzip.decompress(base64.b64decode(m.group(1)))

if extract("PROXY_B64") != open(proxy, "rb").read():
    sys.exit("round-trip mismatch: proxy")
if extract("PLUGIN_B64") != open(plugin, "rb").read():
    sys.exit("round-trip mismatch: plugin")
print("round-trip verified: both payloads identical to source")
PY

BACKUP="$DOC.bak-$(date +%Y%m%d-%H%M%S)"
cp -p "$DOC" "$BACKUP"
chmod +x "$TMP"
mv "$TMP" "$DOC"
trap - EXIT

DOC_HASH="$(hash_file "$DOC")"
DOC_SIZE="$(wc -c < "$DOC" | tr -d ' ')"
say "backup         $BACKUP"
say "doctor         $DOC ($DOC_SIZE bytes)"
say "doctor sha256  $DOC_HASH"

if [[ "$DO_GIST" -eq 0 ]]; then
    say ""
    say "local only. publish with:  $0 --gist"
    exit 0
fi

command -v gh >/dev/null 2>&1 || die "gh not installed; cannot update the gist"
gh auth status >/dev/null 2>&1 || die "gh not authenticated"

say ""
say "updating gist $GIST …"
gh gist edit "$GIST" --filename owp-doctor.sh "$DOC" >/dev/null

REV="$(gh api "gists/$GIST" --jq '.history[0].version')"
URL="https://gist.githubusercontent.com/pritkr/$GIST/raw/$REV/owp-doctor.sh"
PINNED="https://gist.githubusercontent.com/pritkr/$GIST/raw/owp-doctor.sh"

say "revision       $REV"
say "pinned url     $URL"
say "latest url     $PINNED"

# Confirm the raw endpoint serves exactly what we just wrote.
TMPD="$(mktemp -d "${TMPDIR:-/tmp}/owp-verify.XXXXXX")"
trap 'rm -rf "$TMPD"' EXIT
for attempt in 1 2 3 4 5; do
    if curl -fsSL "$URL" -o "$TMPD/doc" 2>/dev/null && [[ "$(hash_file "$TMPD/doc")" == "$DOC_HASH" ]]; then
        say "raw verified   sha256 matches"
        break
    fi
    [[ "$attempt" -eq 5 ]] && die "raw endpoint did not serve the new bytes yet; retry in a minute"
    sleep 3
done

say ""
say "friend runs:"
say "  curl -fsSL $URL -o owp-doctor.sh && chmod +x owp-doctor.sh && sha256sum owp-doctor.sh && ./owp-doctor.sh"
