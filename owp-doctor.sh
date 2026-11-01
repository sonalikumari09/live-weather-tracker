#!/usr/bin/env bash
# ==============================================================================
# owp-doctor.sh — OpenCode WARP proxy: state doctor + deterministic installer
#
#   ./owp-doctor.sh                  diagnose only, changes nothing
#   ./owp-doctor.sh --fix            repair + install pinned files + guard timer
#   ./owp-doctor.sh --on             --fix, then enable the proxy
#   ./owp-doctor.sh --fix --yes      no prompts
#   ./owp-doctor.sh --fix --no-deps  do not touch packages
#
# Never calls a model. `reset` / `test` are not used (they burn free messages).
# Exit: 0 healthy or fixed, 1 broken/unfixed, 2 usage.
# ==============================================================================
LC_ALL=C
export LC_ALL

WARP_PORT=40000
PRIVOXY_PORT=8118
PROXY_URL="http://127.0.0.1:${PRIVOXY_PORT}"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
PRIVOXY_CONF="$CONFIG_DIR/privoxy.conf"
PLUGIN="$CONFIG_DIR/plugins/privacy-shield.js"
BIN_TARGET="$HOME/.local/bin/opencode-proxy"
BIN_LINK="$HOME/.opencode/bin/opencode-proxy"
UNIT_DIR="$HOME/.config/systemd/user"
TMO=6

# Pinned bytes. The installed copies on the author's machine are ahead of
# GitHub main; these hashes are the whole point of "deterministic".
HASH_PROXY=2fe96a31d2d07db1b86019c4869be9e4aa0e04884eab46a5e308b977318c54b1
HASH_PLUGIN=e86457bfa5512a8c3021a10c4a4e96af5cedefd29659957ea152dccae3ccb945

MODE_FIX=0
MODE_ON=0
MODE_YES=0
MODE_DEPS=ask

OKS=0
WARNS=0
FAILS=0
FINDINGS=()

# ------------------------------------------------------------------ helpers ---
bg() { :; }
hdr() { printf '\n=== %s ===\n' "$*"; }
sub() { printf '\n-- %s\n' "$*"; }
ok()   { printf '  [ OK ] %s\n' "$*"; OKS=$((OKS + 1)); }
warn() { printf '  [WARN] %s\n' "$*"; WARNS=$((WARNS + 1)); FINDINGS+=("$*"); }
bad()  { printf '  [FAIL] %s\n' "$*"; FAILS=$((FAILS + 1)); FINDINGS+=("$*"); }
skip() { printf '  [SKIP] %s\n' "$*"; }
info() { printf '  [INFO] %s\n' "$*"; }

have() { command -v "$1" >/dev/null 2>&1; }

tmo() {
    local secs="$1"
    shift
    if have timeout; then timeout "$secs" "$@" 2>&1; else "$@" 2>&1; fi
}

hash_file() {
    if have sha256sum; then sha256sum "$1" 2>/dev/null | awk '{print $1}'
    elif have shasum; then shasum -a 256 "$1" 2>/dev/null | awk '{print $1}'
    else echo unavailable; fi
}

size_of() { wc -c < "$1" 2>/dev/null | tr -d ' '; }

find_opencode() {
    if command -v opencode >/dev/null 2>&1; then command -v opencode
    elif [[ -x "$HOME/.opencode/bin/opencode" ]]; then echo "$HOME/.opencode/bin/opencode"
    elif [[ -x "$HOME/.local/bin/opencode" ]]; then echo "$HOME/.local/bin/opencode"
    elif [[ -x /usr/local/bin/opencode ]]; then echo /usr/local/bin/opencode
    elif [[ -x /usr/bin/opencode ]]; then echo /usr/bin/opencode
    else echo ""; fi
}

port_listen() {
    local p="$1"
    if have ss; then ss -ltnH 2>/dev/null | grep -qE "[:.]${p}[[:space:]]" && return 0; fi
    if have lsof; then lsof -nP -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1 && return 0; fi
    if have nc; then nc -z 127.0.0.1 "$p" >/dev/null 2>&1 && return 0; fi
    return 1
}

port_pids() {
    local p="$1"
    if have lsof; then lsof -nP -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | sort -u | tr '\n' ' ' | sed 's/ $//'; fi
}

field() {
    sed -n "s/^$1=//p" 2>/dev/null | head -1
}

trace_direct() { curl -s --max-time "$TMO" https://cloudflare.com/cdn-cgi/trace 2>/dev/null; }
trace_proxy()  { curl -s --max-time "$TMO" -x "$PROXY_URL" https://cloudflare.com/cdn-cgi/trace 2>/dev/null; }

warp_bin() {
    if have warp-cli; then command -v warp-cli
    elif [[ -x /usr/bin/warp-cli ]]; then echo /usr/bin/warp-cli
    else echo ""; fi
}

warp_run() {
    local w
    w="$(warp_bin)"
    [[ -n "$w" ]] || return 1
    "$w" "$@" 2>&1
}

usage() {
    sed -n '3,12p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//'
    exit 2
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix) MODE_FIX=1 ;;
        --on) MODE_ON=1; MODE_FIX=1 ;;
        --yes|-y) MODE_YES=1 ;;
        --no-deps) MODE_DEPS=no ;;
        --deps) MODE_DEPS=yes ;;
        --help|-h) usage ;;
        *) echo "unknown flag: $1" >&2; usage ;;
    esac
    shift
done

OC_BIN="$(find_opencode)"
SCRIPT_HASH="$(hash_file "$0" 2>/dev/null)"

# =============================================================== DIAGNOSIS ====
hdr "0. Host"
printf '  date        %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z' 2>/dev/null)"
printf '  kernel      %s\n' "$(uname -srm)"
if [[ -r /etc/os-release ]]; then
    printf '  distro      %s\n' "$(sed -n 's/^PRETTY_NAME=//p' /etc/os-release | tr -d '"')"
elif [[ -r /etc/fedora-release ]]; then
    printf '  distro      %s\n' "$(cat /etc/fedora-release)"
else
    printf '  distro      %s\n' "not /etc/os-release"
fi
printf '  user        %s (uid %s)\n' "$(id -un)" "$(id -u)"
printf '  home        %s\n' "$HOME"
printf '  shell       %s\n' "${SHELL:-unknown}"
printf '  bash        %s\n' "${BASH_VERSION:-unknown}"
printf '  script hash %s\n' "$SCRIPT_HASH"
if have systemctl && systemctl --user show-environment >/dev/null 2>&1; then
    printf '  systemd     user manager reachable\n'
else
    printf '  systemd     user manager NOT reachable\n'
fi
if have gzip && have base64; then :; else
    bad "gzip/base64 missing — the embedded payload cannot be unpacked"
fi

# --- 1. OpenCode -------------------------------------------------------------
hdr "1. OpenCode"
if [[ -z "$OC_BIN" ]]; then
    bad "opencode binary not found (PATH, ~/.opencode/bin, ~/.local/bin, /usr/local/bin, /usr/bin)"
else
    ok "binary: $OC_BIN"
    printf '  version     %s\n' "$(tmo 10 "$OC_BIN" --version 2>/dev/null | head -1)"
fi
OPIDS="$(pgrep -f "opencode (serve|tui)" 2>/dev/null | head -5)"
if [[ -n "$OPIDS" ]]; then
    info "processes:"
    for pid in $OPIDS; do
        ps -p "$pid" -o pid=,etime=,args= 2>/dev/null | cut -c1-120 | sed 's/^/          /'
    done
else
    skip "no running opencode server/tui"
fi
if [[ -d "$CONFIG_DIR" ]]; then
    ok "config dir: $CONFIG_DIR"
    printf '  files       %s\n' "$(ls -1 "$CONFIG_DIR" 2>/dev/null | tr '\n' ' ')"
else
    warn "config dir missing: $CONFIG_DIR"
fi

# --- 2. service env (the usual culprit) --------------------------------------
hdr "2. OpenCode service environment (persistent across reboots)"
ENV_JSON=""
ENV_HAS_PROXY=0
if [[ -n "$OC_BIN" ]]; then
    ENV_JSON="$(tmo 10 "$OC_BIN" service get env 2>/dev/null)"
    printf '  service get env:\n'
    if [[ -n "$ENV_JSON" ]]; then printf '%s\n' "$ENV_JSON" | sed 's/^/          /'; else printf '          (empty)\n'; fi
    if printf '%s' "$ENV_JSON" | grep -q "${PRIVOXY_PORT}"; then ENV_HAS_PROXY=1; fi
    if [[ "$ENV_HAS_PROXY" -eq 1 ]]; then
        warn "service pins traffic to ${PROXY_URL} — if 8118 is down, EVERY provider fails"
    else
        ok "no proxy pinned in service env"
    fi
else
    skip "no opencode binary — cannot read service env"
fi

sub "shell environment"
SH_ENV="$(env 2>/dev/null | grep -iE '^(HTTPS?_PROXY|ALL_PROXY|NO_PROXY)=' | sort)"
if [[ -n "$SH_ENV" ]]; then
    printf '%s\n' "$SH_ENV" | sed 's/^/          /'
    warn "proxy variables present in this shell (affects every child process)"
else
    ok "no proxy variables in this shell"
fi

sub "shell rc leftovers"
RC_HITS=0
for rc in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile" "$HOME/.zshrc"; do
    [[ -f "$rc" ]] || continue
    if grep -qiE 'proxy|8118|40000' "$rc" 2>/dev/null; then
        printf '          %s:\n' "$rc"
        grep -niE 'proxy|8118|40000' "$rc" 2>/dev/null | head -5 | sed 's/^/            /'
        RC_HITS=$((RC_HITS + 1))
    fi
done
if [[ "$RC_HITS" -eq 0 ]]; then ok "no proxy lines in shell rc files"; else warn "proxy lines in $RC_HITS rc file(s)"; fi

sub "service.json (secrets redacted)"
if [[ -f "$CONFIG_DIR/service.json" ]]; then
    sed -E 's/("password"[[:space:]]*:[[:space:]]*")[^"]*/\1REDACTED/' "$CONFIG_DIR/service.json" \
        2>/dev/null | sed 's/^/          /'
    ok "service.json present"
else
    skip "no service.json"
fi

# --- 3. Privoxy --------------------------------------------------------------
hdr "3. Privoxy (${PROXY_URL} -> WARP SOCKS5 127.0.0.1:${WARP_PORT})"
P8118=0
port_listen "$PRIVOXY_PORT" && P8118=1
if have privoxy; then
    ok "binary: $(command -v privoxy) ($(privoxy --version 2>/dev/null | head -1 | cut -c1-60))"
else
    bad "privoxy not installed (dnf install -y privoxy)"
fi
if [[ -f "$PRIVOXY_CONF" ]]; then
    ok "config: $PRIVOXY_CONF ($(size_of "$PRIVOXY_CONF") bytes)"
    if grep -q "forward-socks5 / 127.0.0.1:${WARP_PORT}" "$PRIVOXY_CONF" 2>/dev/null; then
        ok "config forwards to WARP on ${WARP_PORT}"
    else
        bad "config does NOT forward to 127.0.0.1:${WARP_PORT} — traffic exits direct or dies"
    fi
else
    warn "config missing: $PRIVOXY_CONF (written by 'opencode-proxy on')"
fi
if [[ "$P8118" -eq 1 ]]; then
    ok "port ${PRIVOXY_PORT} listening (pid: $(port_pids "$PRIVOXY_PORT"))"
    PROC="$(ps -p "$(port_pids "$PRIVOXY_PORT" | awk '{print $1}')" -o comm= 2>/dev/null)"
    [[ -n "$PROC" ]] && printf '          owner: %s\n' "$PROC"
else
    if [[ "$ENV_HAS_PROXY" -eq 1 ]]; then
        bad "port ${PRIVOXY_PORT} NOT listening but service env points at it — this breaks every model"
    else
        info "port ${PRIVOXY_PORT} not listening (fine while proxy is off)"
    fi
fi
if have systemctl; then
    ENABLED="$(systemctl is-enabled privoxy 2>/dev/null | head -1)"
    ACTIVE="$(systemctl is-active privoxy 2>/dev/null | head -1)"
    printf '  unit        enabled=%s active=%s\n' "${ENABLED:-unknown}" "${ACTIVE:-unknown}"
    if [[ "$ENABLED" == "enabled" || "$ACTIVE" == "active" ]]; then
        warn "distro privoxy.service owns 8118 — it uses /etc/privoxy/config, not the WARP bridge"
    fi
fi

# --- 4. WARP ----------------------------------------------------------------
hdr "4. Cloudflare WARP"
WARP_CONN=0
WARP_MODE_OK=0
P40000=0
port_listen "$WARP_PORT" && P40000=1
if [[ -n "$(warp_bin)" ]]; then
    ok "binary: $(warp_bin)"
    printf '  version     %s\n' "$(warp_run --version 2>/dev/null | head -1 | cut -c1-60)"
    WSTAT="$(warp_run status 2>/dev/null)"
    printf '  status      %s\n' "$(printf '%s' "$WSTAT" | tr '\n' ' ' | cut -c1-140)"
    printf '%s' "$WSTAT" | grep -q "Connected" && WARP_CONN=1
    if printf '%s' "$WSTAT" | grep -qi "registration missing\|not registered"; then
        warn "client not registered (warp-cli --accept-tos registration new)"
    fi
    MODE_LINE="$(warp_run settings 2>/dev/null | grep -iE '^[[:space:]]*Mode:' | head -1)"
    printf '  settings    %s\n' "${MODE_LINE:-'(no Mode line)'}"
    if printf '%s' "$MODE_LINE" | grep -qi "WarpProxy"; then
        WARP_MODE_OK=1
        ok "proxy mode configured"
    elif printf '%s' "$MODE_LINE" | grep -qi "Warp"; then
        bad "client is in FULL-TUNNEL mode — that routes the whole machine, not just OpenCode"
    else
        warn "proxy mode not confirmed from settings (falling back to listener)"
        [[ "$P40000" -eq 1 ]] && WARP_MODE_OK=1
    fi
    if [[ "$P40000" -eq 1 ]]; then ok "SOCKS listener on ${WARP_PORT}"; else warn "nothing listening on ${WARP_PORT}"; fi
else
    bad "warp-cli not installed (Cloudflare WARP is required)"
fi

sub "egress"
DTRACE="$(trace_direct)"
D_IP="$(printf '%s' "$DTRACE" | field ip)"
D_WARP="$(printf '%s' "$DTRACE" | field warp)"
D_LOC="$(printf '%s' "$DTRACE" | field loc)"
if [[ -n "$D_IP" ]]; then ok "direct: ip=${D_IP} warp=${D_WARP:-?} loc=${D_LOC:-?}"; else warn "direct trace failed (no internet?)"; fi
PTRACE="$(trace_proxy)"
P_IP="$(printf '%s' "$PTRACE" | field ip)"
P_WARP="$(printf '%s' "$PTRACE" | field warp)"
PROXY_WARP=0
[[ "$P_WARP" == "on" ]] && PROXY_WARP=1
if [[ -n "$P_IP" ]]; then
    printf '  via proxy   ip=%s warp=%s\n' "$P_IP" "${P_WARP:-?}"
    if [[ "$PROXY_WARP" -eq 1 ]]; then ok "8118 egress confirmed through WARP"; else
        if [[ "$P8118" -eq 1 ]]; then bad "8118 is up but NOT egressing through WARP"; else info "no proxy egress (nothing on 8118)"; fi
    fi
else
    if [[ "$P8118" -eq 1 ]]; then bad "proxy trace through 8118 failed"; else info "no proxy trace (8118 down)"; fi
fi

# --- 5. plugin --------------------------------------------------------------
hdr "5. Privacy-shield plugin"
COPIES=()
while IFS= read -r f; do [[ -n "$f" ]] && COPIES+=("$f"); done < <(
    for d in "$CONFIG_DIR/plugins" "$HOME/.config/opencode/plugins" "$HOME/.opencode/plugins"; do
        [[ -d "$d" ]] && find "$d" -maxdepth 1 -name 'privacy-shield.js' -type f 2>/dev/null
    done | sort -u
)
if [[ ${#COPIES[@]} -eq 0 ]]; then
    warn "privacy-shield.js not found (privacy hooks inactive)"
else
    for f in "${COPIES[@]}"; do
        h="$(hash_file "$f")"
        sz="$(size_of "$f")"
        cls="unknown"
        if grep -q 'MIN_MESSAGES_TO_RESUME' "$f" 2>/dev/null; then cls="fixed (one resume per chat, needs sqlite3)"
        elif grep -q 'MAX_RETRIES = 12' "$f" 2>/dev/null; then cls="LEGACY (12 resumes / 10 min loop)"
        elif grep -q 'RESUME_TEXT' "$f" 2>/dev/null; then cls="legacy auto-resume"
        else cls="no auto-resume"; fi
        printf '  %s\n    %s bytes  %s\n    %s\n' "$f" "$sz" "${h:0:16}…" "$cls"
        if [[ "$h" == "$HASH_PLUGIN" ]]; then ok "matches pinned build"; else warn "does not match pinned build"; fi
    done
    if [[ ${#COPIES[@]} -gt 1 ]]; then
        bad "${#COPIES[@]} copies — OpenCode loads each one, hooks register twice"
    else
        ok "exactly one copy"
    fi
fi
sub "other plugin files"
OTHER="$(for d in "$CONFIG_DIR/plugins" "$HOME/.opencode/plugins"; do
    [[ -d "$d" ]] && find "$d" -maxdepth 1 -type f 2>/dev/null
done | sort -u)"
if [[ -n "$OTHER" ]]; then
    printf '%s\n' "$OTHER" | sed 's/^/          /'
    printf '%s' "$OTHER" | grep -q 'auto-resume.js$' && warn "auto-resume.js present (retired; remove it)"
else
    skip "none"
fi

# --- 6. leftovers -----------------------------------------------------------
hdr "6. Installed artefacts"
if [[ -f "$BIN_TARGET" ]]; then
    BH="$(hash_file "$BIN_TARGET")"
    printf '  %s\n    %s bytes  %s\n' "$BIN_TARGET" "$(size_of "$BIN_TARGET")" "${BH:0:16}…"
    [[ -x "$BIN_TARGET" ]] && ok "executable" || bad "not executable"
    if [[ "$BH" == "$HASH_PROXY" ]]; then ok "matches pinned build"; else warn "differs from pinned build (legacy 36KB build embeds the old plugin)"; fi
else
    warn "$BIN_TARGET missing"
fi
if [[ -L "$BIN_LINK" ]]; then
    ok "$BIN_LINK -> $(readlink "$BIN_LINK")"
elif [[ -f "$BIN_LINK" ]]; then
    warn "$BIN_LINK is a real file (will drift from $BIN_TARGET)"
else
    info "$BIN_LINK missing"
fi
BAKS="$(find "$HOME/.local/bin" -maxdepth 1 -name 'opencode-proxy.bak-*' 2>/dev/null | wc -l | tr -d ' ')"
[[ "$BAKS" != "0" ]] && info "$BAKS backup file(s) in ~/.local/bin (harmless)"
sub "scheduled jobs"
CRON="$(crontab -l 2>/dev/null | grep -i 'opencode-proxy' || true)"
[[ -n "$CRON" ]] && printf '%s\n' "$CRON" | sed 's/^/          /' || skip "no crontab entry"
if [[ -f "$UNIT_DIR/opencode-proxy-guard.timer" ]]; then
    ok "guard timer file present"
    if have systemctl; then printf '  timer       %s\n' "$(systemctl --user is-active opencode-proxy-guard.timer 2>/dev/null)"; fi
else
    warn "no guard timer — after a reboot nothing restarts privoxy while service env still points at 8118"
fi

# --- 7. connectivity --------------------------------------------------------
hdr "7. Connectivity (no model calls, no quota spent)"
if have getent; then
    DNS="$(getent hosts opencode.ai 2>/dev/null | head -1)"
    [[ -n "$DNS" ]] && ok "dns opencode.ai -> ${DNS%% *}" || bad "dns lookup failed for opencode.ai"
fi
CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time "$TMO" https://opencode.ai 2>/dev/null)"
if [[ "$CODE" =~ ^[23] ]]; then ok "direct https opencode.ai -> $CODE"; else warn "direct https opencode.ai -> ${CODE:-no response}"; fi
if [[ "$P8118" -eq 1 ]]; then
    PCODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time "$TMO" -x "$PROXY_URL" https://opencode.ai 2>/dev/null)"
    if [[ "$PCODE" =~ ^[23] ]]; then ok "proxied https opencode.ai -> $PCODE"; else bad "proxied https opencode.ai -> ${PCODE:-no response}"; fi
else
    info "proxied check skipped (8118 down)"
fi

sub "recent log lines"
NEWEST="$(ls -t "$HOME"/.local/share/opencode/log/*.log 2>/dev/null | head -1)"
if [[ -n "$NEWEST" ]]; then
    printf '  %s\n' "$NEWEST"
    grep -iE '8118|ECONNREFUSED|ECONNRESET|ETIMEDOUT|Free usage limit|proxy (error|refused)' "$NEWEST" 2>/dev/null \
        | tail -6 | cut -c1-160 | sed 's/^/          /'
    [[ -z "$(grep -iE '8118|ECONNREFUSED|ECONNRESET|ETIMEDOUT|Free usage limit|proxy (error|refused)' "$NEWEST" 2>/dev/null)" ]] && info "(no matching lines)"
else
    skip "no log file yet"
fi

# ================================================================= VERDICT ====
hdr "VERDICT"
STATE="UNKNOWN"
if [[ "$WARP_CONN" -eq 1 && "$WARP_MODE_OK" -eq 0 && -n "$(warp_bin)" ]]; then
    STATE="BROKEN_FULLTUNNEL"
elif [[ "$ENV_HAS_PROXY" -eq 1 && "$P8118" -eq 0 ]]; then
    STATE="BROKEN_PHANTOM_ENV"
elif [[ "$ENV_HAS_PROXY" -eq 1 && "$P8118" -eq 1 && "$PROXY_WARP" -eq 0 ]]; then
    STATE="BROKEN_DEAD_FORWARD"
elif [[ "$ENV_HAS_PROXY" -eq 1 && "$PROXY_WARP" -eq 1 ]]; then
    STATE="HEALTHY_PROXY_ON"
elif [[ "$ENV_HAS_PROXY" -eq 0 ]]; then
    STATE="HEALTHY_PROXY_OFF"
fi

case "$STATE" in
    BROKEN_FULLTUNNEL)
        bad "state: FULL-TUNNEL WARP — all system traffic is routed, not just OpenCode"
        printf '         Every app breaks, any model fails. Fix: warp-cli disconnect\n' ;;
    BROKEN_PHANTOM_ENV)
        bad "state: PHANTOM PROXY — service env points at 8118, nothing is listening"
        printf '         This is the \"nothing works on any model\" failure. Fix: unset env + restart\n' ;;
    BROKEN_DEAD_FORWARD)
        bad "state: DEAD FORWARD — 8118 listens but does not egress through WARP"
        printf '         Typical cause: distro privoxy.service on /etc/privoxy/config, or WARP down\n' ;;
    HEALTHY_PROXY_ON)
        ok "state: proxy ON and routing through WARP" ;;
    HEALTHY_PROXY_OFF)
        ok "state: proxy OFF, direct connection" ;;
    *)
        warn "state: inconclusive (missing binaries above)" ;;
esac
printf '  counts      ok=%s warn=%s fail=%s\n' "$OKS" "$WARNS" "$FAILS"

PROXY_B64='
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
'
PLUGIN_B64='
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
'

# ==================================================================== FIX ====
if [[ "$MODE_FIX" -eq 1 ]]; then
    hdr "FIX PLAN"
    printf '  1. back up service.json, service env, plugin, privoxy config, crontab\n'
    printf '  2. stop stale privoxy on %s (user unit, distro unit, stray pid)\n' "$PRIVOXY_PORT"
    printf '  3. unset HTTPS_PROXY/HTTP_PROXY/ALL_PROXY/NO_PROXY from the OpenCode service\n'
    printf '  4. remove duplicate/stale plugin copies\n'
    printf '  5. install pinned opencode-proxy + privacy-shield.js (hash-gated)\n'
    printf '  6. install + enable the systemd user guard timer\n'
    if [[ "$MODE_DEPS" != "no" ]]; then printf '  7. install missing packages: privoxy, lsof, sqlite, gzip, cloudflare-warp\n'; fi
    if [[ "$MODE_ON" -eq 1 ]]; then printf '  8. enable the proxy (opencode-proxy on)\n'; else printf '  8. leave the proxy OFF\n'; fi
    if [[ "$MODE_YES" -eq 0 ]]; then
        printf '\nProceed? [y/N] '
        REPLY=""
        if [[ -t 0 ]]; then read -r REPLY; else read -r REPLY < /dev/tty 2>/dev/null || REPLY=""; fi
        case "$REPLY" in y|Y|yes|YES) ;; *) echo "aborted"; exit 1 ;; esac
    fi

    BK="$HOME/.local/state/owp-doctor/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BK" || { bad "cannot create backup dir $BK"; exit 1; }
    hdr "BACKUP -> $BK"
    [[ -f "$CONFIG_DIR/service.json" ]] && cp -p "$CONFIG_DIR/service.json" "$BK/" 2>/dev/null
    [[ -n "$OC_BIN" ]] && tmo 10 "$OC_BIN" service get env > "$BK/service-env.json" 2>/dev/null
    [[ -f "$PRIVOXY_CONF" ]] && cp -p "$PRIVOXY_CONF" "$BK/" 2>/dev/null
    [[ -f "$PLUGIN" ]] && cp -p "$PLUGIN" "$BK/" 2>/dev/null
    crontab -l > "$BK/crontab.txt" 2>/dev/null
    for u in opencode-proxy-guard.service opencode-proxy-guard.timer; do
        [[ -f "$UNIT_DIR/$u" ]] && cp -p "$UNIT_DIR/$u" "$BK/" 2>/dev/null
    done
    ok "saved $(ls -1 "$BK" 2>/dev/null | wc -l | tr -d ' ') file(s)"

    SUDO=""
    if [[ "$(id -u)" -eq 0 ]]; then SUDO=""
    elif have sudo; then
        if sudo -n true 2>/dev/null; then SUDO="sudo -n"
        elif [[ -t 0 || -t 1 ]]; then SUDO="sudo"; fi
    fi

    if [[ "$MODE_DEPS" != "no" ]]; then
        hdr "PACKAGES"
        if [[ -z "$SUDO" && "$(id -u)" -ne 0 ]]; then
            skip "no sudo available — install manually: sudo dnf install -y privoxy lsof sqlite gzip"
        else
            MISSING=""
            have privoxy || MISSING="$MISSING privoxy"
            have lsof || MISSING="$MISSING lsof"
            have sqlite3 || MISSING="$MISSING sqlite"
            have gzip || MISSING="$MISSING gzip"
            have curl || MISSING="$MISSING curl"
            if [[ -n "$MISSING" ]]; then
                info "dnf install -y$MISSING"
                $SUDO dnf install -y $MISSING >/dev/null 2>&1 && ok "installed$MISSING" || warn "dnf install failed for$MISSING"
            else
                ok "privoxy/lsof/sqlite/gzip/curl present"
            fi
            if ! have warp-cli; then
                info "adding Cloudflare WARP repo + installing cloudflare-warp"
                $SUDO rpm --import https://pkg.cloudflareclient.com/pubkey.gpg >/dev/null 2>&1
                printf '[cloudflare-warp]\nname=cloudflare-warp\nbaseurl=https://pkg.cloudflareclient.com/\nenabled=1\ngpgcheck=1\ngpgkey=https://pkg.cloudflareclient.com/pubkey.gpg\n' \
                    | $SUDO tee /etc/yum.repos.d/cloudflare-warp.repo >/dev/null 2>&1
                $SUDO dnf install -y cloudflare-warp >/dev/null 2>&1 && ok "cloudflare-warp installed" || warn "cloudflare-warp install failed"
                $SUDO systemctl enable --now warp-svc >/dev/null 2>&1 || true
            else
                ok "warp-cli present"
            fi
        fi
    fi

    hdr "STOP STALE PRIVOXY"
    if have systemctl; then
        systemctl --user stop privoxy >/dev/null 2>&1 || true
        if [[ -n "$SUDO" ]]; then $SUDO systemctl disable --now privoxy >/dev/null 2>&1 || true; fi
    fi
    if [[ "$P8118" -eq 1 ]]; then
        for pid in $(port_pids "$PRIVOXY_PORT"); do
            owner="$(ps -p "$pid" -o comm= 2>/dev/null)"
            if printf '%s' "$owner" | grep -qi privoxy; then
                kill "$pid" 2>/dev/null && info "killed privoxy pid $pid on ${PRIVOXY_PORT}" || true
            else
                warn "port ${PRIVOXY_PORT} owned by '${owner:-unknown}' pid $pid — not killing it"
            fi
        done
    fi
    sleep 1
    if port_listen "$PRIVOXY_PORT"; then warn "something still listens on ${PRIVOXY_PORT}"; else ok "port ${PRIVOXY_PORT} free"; fi

    hdr "CLEAR SERVICE PROXY ENV"
    if [[ -n "$OC_BIN" ]]; then
        for v in HTTPS_PROXY HTTP_PROXY ALL_PROXY NO_PROXY; do
            tmo 10 "$OC_BIN" service unset env "$v" >/dev/null 2>&1 || true
        done
        tmo 20 "$OC_BIN" service restart >/dev/null 2>&1 || true
        AFTER="$(tmo 10 "$OC_BIN" service get env 2>/dev/null)"
        if printf '%s' "$AFTER" | grep -q "${PRIVOXY_PORT}"; then
            bad "service env still references ${PRIVOXY_PORT}"
        else
            ok "service env clean: $(printf '%s' "$AFTER" | tr -d '\n' | cut -c1-60)"
        fi
    else
        skip "no opencode binary"
    fi

    hdr "PLUGIN HYGIENE"
    for stale in "$HOME/.opencode/plugins/privacy-shield.js" "$HOME/.config/opencode/plugins/auto-resume.js" "$HOME/.opencode/plugins/auto-resume.js"; do
        if [[ -f "$stale" ]]; then rm -f "$stale" && ok "removed $stale"; fi
    done
    for d in "$HOME/.opencode/plugins" "$HOME/.config/opencode/plugins"; do
        [[ -d "$d" ]] && ok "watching $d: $(ls -1 "$d" 2>/dev/null | tr '\n' ' ')"
    done

    hdr "INSTALL PINNED FILES"
    TMPD="$(mktemp -d 2>/dev/null || echo "/tmp/owp.$$")"
    mkdir -p "$TMPD"
    decode_ok=1
    printf '%s' "$PROXY_B64" | base64 -d 2>/dev/null | gzip -dc > "$TMPD/opencode-proxy" 2>/dev/null || decode_ok=0
    printf '%s' "$PLUGIN_B64" | base64 -d 2>/dev/null | gzip -dc > "$TMPD/privacy-shield.js" 2>/dev/null || decode_ok=0
    if [[ "$decode_ok" -ne 1 ]]; then
        bad "payload decode failed"
    else
        for pair in "opencode-proxy:$HASH_PROXY" "privacy-shield.js:$HASH_PLUGIN"; do
            f="${pair%%:*}"; want="${pair##*:}"
            got="$(hash_file "$TMPD/$f")"
            if [[ "$got" == "$want" ]]; then ok "verified $f"; else bad "$f hash mismatch ($got)"; decode_ok=0; fi
        done
    fi
    if [[ "$decode_ok" -eq 1 ]]; then
        mkdir -p "$HOME/.local/bin" "$HOME/.opencode/bin" "$(dirname "$PLUGIN")"
        install -m 755 "$TMPD/opencode-proxy" "$BIN_TARGET" && ok "installed $BIN_TARGET" || bad "install failed"
        install -m 644 "$TMPD/privacy-shield.js" "$PLUGIN" && ok "installed $PLUGIN" || bad "install failed"
        ln -sfn "$BIN_TARGET" "$BIN_LINK" && ok "linked $BIN_LINK"
    fi
    rm -rf "$TMPD"

    hdr "GUARD TIMER"
    mkdir -p "$UNIT_DIR"
    cat > "$UNIT_DIR/opencode-proxy-guard.service" <<'UNIT'
[Unit]
Description=OpenCode WARP proxy guard

[Service]
Type=oneshot
ExecStart=%h/.local/bin/opencode-proxy guard
UNIT
    cat > "$UNIT_DIR/opencode-proxy-guard.timer" <<'UNIT'
[Unit]
Description=OpenCode WARP proxy guard timer

[Timer]
OnStartupSec=30s
OnUnitActiveSec=15min
Persistent=true
Unit=opencode-proxy-guard.service

[Install]
WantedBy=timers.target
UNIT
    if have systemctl && systemctl --user show-environment >/dev/null 2>&1; then
        systemctl --user daemon-reload >/dev/null 2>&1 || true
        systemctl --user enable --now opencode-proxy-guard.timer >/dev/null 2>&1 \
            && ok "timer enabled" || warn "could not enable timer"
        loginctl enable-linger "$(id -un)" >/dev/null 2>&1 && ok "linger enabled" || info "linger not enabled (timer stops at logout)"
    else
        warn "no systemd user manager — add a cron entry instead:"
        printf '          */15 * * * * %s guard >/dev/null 2>&1\n' "$BIN_TARGET"
    fi

    if [[ "$MODE_ON" -eq 1 ]]; then
        hdr "ENABLE PROXY"
        W="$(warp_bin)"
        if [[ -z "$W" ]]; then
            bad "warp-cli missing — cannot enable"
        else
            WS="$($W status 2>&1)"
            if printf '%s' "$WS" | grep -qi "registration missing\|not registered"; then
                $W --accept-tos registration new >/dev/null 2>&1 && ok "registered WARP client" || warn "registration failed"
            else
                ok "WARP client registered"
            fi
            if [[ -x "$BIN_TARGET" ]]; then
                if "$BIN_TARGET" on; then ok "proxy enabled"; else bad "opencode-proxy on failed (see output above)"; fi
            else
                bad "$BIN_TARGET missing"
            fi
        fi
    else
        hdr "PROXY LEFT OFF"
        info "everything now runs direct; enable later with: $BIN_TARGET on"
    fi
fi

# --------------------------------------------------------------- re-verify ---
hdr "FINAL STATE"
F_P8118=0; port_listen "$PRIVOXY_PORT" && F_P8118=1
F_P40000=0; port_listen "$WARP_PORT" && F_P40000=1
F_ENV=0
if [[ -n "$OC_BIN" ]]; then
    F_JSON="$(tmo 10 "$OC_BIN" service get env 2>/dev/null)"
    printf '%s' "$F_JSON" | grep -q "${PRIVOXY_PORT}" && F_ENV=1
    printf '  service env %s\n' "$(printf '%s' "$F_JSON" | tr -d '\n' | cut -c1-80)"
fi
F_WARP=0; [[ -n "$(warp_bin)" ]] && warp_run status 2>/dev/null | grep -q Connected && F_WARP=1
F_TRACE="$(printf '%s' "$(trace_proxy)" | field warp)"
printf '  8118=%s 40000=%s warp_connected=%s proxy_warp=%s env_pinned=%s\n' \
    "$F_P8118" "$F_P40000" "$F_WARP" "${F_TRACE:-?}" "$F_ENV"
FINAL_BAD=0
if [[ "$F_ENV" -eq 1 && "$F_P8118" -eq 0 ]]; then
    bad "still inconsistent: env pinned to a dead proxy"; FINAL_BAD=1
elif [[ "$F_ENV" -eq 0 && "$F_P8118" -eq 0 ]]; then
    ok "direct mode — every provider should work"
elif [[ "$F_ENV" -eq 1 && "$F_TRACE" == "on" ]]; then
    ok "proxy mode — routing through WARP"
elif [[ "$F_ENV" -eq 1 ]]; then
    bad "env pinned and 8118 up, but egress is not WARP"; FINAL_BAD=1
else
    info "proxy running but env not pinned (harmless; 'opencode-proxy on' re-pins)"
fi

hdr "NEXT"
if [[ "$MODE_FIX" -eq 0 ]]; then
    printf '  read-only run. To repair + install: %s --fix\n' "$0"
    printf '  to also enable the proxy:          %s --on\n' "$0"
else
    printf '  %s on|off|status\n' "$BIN_TARGET"
    printf '  never run \"reset\" casually: it probes with real messages (up to 8).\n'
fi
if [[ ${#FINDINGS[@]} -gt 0 ]]; then
    if [[ "$MODE_FIX" -eq 1 ]]; then
        printf '\n  findings present before the fix:\n'
    else
        printf '\n  open findings:\n'
    fi
    for f in "${FINDINGS[@]}"; do printf '    - %s\n' "$f"; done
fi

if [[ "$FINAL_BAD" -eq 1 ]]; then exit 1; fi
if [[ "$MODE_FIX" -eq 0 && "$FAILS" -gt 0 ]]; then exit 1; fi
exit 0
