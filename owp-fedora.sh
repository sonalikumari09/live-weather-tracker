#!/usr/bin/env bash
# ==============================================================================
# owp-fedora.sh — ONE file. Updates opencode-proxy + plugin on Fedora,
#                 repairs WARP (daemon, registration, proxy mode, port 40000),
#                 installs the boot guard, and runs a reset that cannot
#                 leave the machine with a phantom proxy.
#
# No owp-doctor.sh, no gist, no repo needed. Payloads are embedded and
# hash-gated.
#
#   ./owp-fedora.sh --check     read-only report, changes nothing
#   ./owp-fedora.sh             install/update files + guard, keep proxy OFF
#   ./owp-fedora.sh --on        same, then enable the proxy
#   ./owp-fedora.sh --reset     same, then run the SAFE reset (spends quota)
#   ./owp-fedora.sh --yes       no prompts
#   ./owp-fedora.sh --no-deps   never touch packages
#
# Exit: 0 ok, 1 broken/failed, 2 usage.
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

HASH_PROXY=2fe96a31d2d07db1b86019c4869be9e4aa0e04884eab46a5e308b977318c54b1
HASH_PLUGIN=e86457bfa5512a8c3021a10c4a4e96af5cedefd29659957ea152dccae3ccb945

MODE=install
ASSUME_YES=0
DEPS=ask

for arg in "$@"; do
    case "$arg" in
        --check) MODE=check ;;
        --install) MODE=install ;;
        --on) MODE=on ;;
        --reset) MODE=reset ;;
        --yes|-y) ASSUME_YES=1 ;;
        --no-deps) DEPS=no ;;
        --deps) DEPS=yes ;;
        --help|-h) sed -n '3,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown flag: $arg" >&2; exit 2 ;;
    esac
done

# ------------------------------------------------------------------ helpers ---
hdr() { printf '\n=== %s ===\n' "$*"; }
ok() { printf '  [ OK ] %s\n' "$*"; }
warn() { printf '  [WARN] %s\n' "$*"; }
bad() { printf '  [FAIL] %s\n' "$*"; }
info() { printf '  [INFO] %s\n' "$*"; }
skip() { printf '  [SKIP] %s\n' "$*"; }
die() { bad "$*"; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

tmo() { local s="$1"; shift; if have timeout; then timeout "$s" "$@" 2>&1; else "$@" 2>&1; fi; }

hash_file() {
    if have sha256sum; then sha256sum "$1" 2>/dev/null | awk '{print $1}'
    elif have shasum; then shasum -a 256 "$1" 2>/dev/null | awk '{print $1}'
    else echo unavailable; fi
}

find_opencode() {
    if command -v opencode >/dev/null 2>&1; then command -v opencode
    elif [[ -x "$HOME/.opencode/bin/opencode" ]]; then echo "$HOME/.opencode/bin/opencode"
    elif [[ -x "$HOME/.local/bin/opencode" ]]; then echo "$HOME/.local/bin/opencode"
    elif [[ -x /usr/local/bin/opencode ]]; then echo /usr/local/bin/opencode
    elif [[ -x /usr/bin/opencode ]]; then echo /usr/bin/opencode
    else echo ""; fi
}

warp_bin() {
    if have warp-cli; then command -v warp-cli
    elif [[ -x /usr/bin/warp-cli ]]; then echo /usr/bin/warp-cli
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
    have lsof || return 0
    lsof -nP -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | sort -u | tr '\n' ' ' | sed 's/ $//'
}

field() { sed -n "s/^$1=//p" 2>/dev/null | head -1; }
trace_direct() { curl -s --max-time "$TMO" https://cloudflare.com/cdn-cgi/trace 2>/dev/null; }
trace_proxy() { curl -s --max-time "$TMO" -x "$PROXY_URL" https://cloudflare.com/cdn-cgi/trace 2>/dev/null; }

confirm() {
    [[ "$ASSUME_YES" -eq 1 ]] && return 0
    printf '\n%s [y/N] ' "$1"
    local reply=""
    if [[ -t 0 ]]; then read -r reply; else read -r reply < /dev/tty 2>/dev/null || reply=""; fi
    case "$reply" in y|Y|yes|YES) return 0 ;; *) return 1 ;; esac
}

SUDO=""
if [[ "$(id -u)" -eq 0 ]]; then SUDO=""
elif have sudo; then
    if sudo -n true 2>/dev/null; then SUDO="sudo -n"
    elif [[ -t 0 || -t 1 ]]; then SUDO="sudo"; fi
fi

OC_BIN="$(find_opencode)"
WARP_CLI="$(warp_bin)"

# ---------------------------------------------------------------------- WARP ---
# opencode-proxy only asks WARP for proxy mode and then waits 10s. If warp-svc
# is down, or the client was never registered, every command fails silently and
# the only symptom is "WARP proxy port 40000 is unavailable". Do the privileged
# repair here, and print the real error when it still fails.
WARP_LAST_ERR=""

warp_run() {
    local out
    out="$("$WARP_CLI" "$@" 2>&1)" && { WARP_LAST_ERR=""; return 0; }
    if [[ -n "$SUDO" ]]; then
        out="$($SUDO "$WARP_CLI" "$@" 2>&1)" && { WARP_LAST_ERR=""; return 0; }
    fi
    WARP_LAST_ERR="$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-200)"
    return 1
}

warp_tos() {
    # --accept-tos is a global flag; older builds only accept the bare form.
    warp_run --accept-tos "$@" && return 0
    [[ -t 0 ]] && warp_run "$@" && return 0
    return 1
}

warp_daemon_up() {
    [[ -n "$WARP_CLI" ]] || return 1
    tmo 10 "$WARP_CLI" status >/dev/null 2>&1
}

warp_daemon_start() {
    warp_daemon_up && return 0
    if ! have systemctl; then
        warn "warp-svc is down and systemctl is unavailable"
        return 1
    fi
    if [[ -z "$SUDO" && "$(id -u)" -ne 0 ]]; then
        warn "warp-svc is down and sudo is unavailable"
        info "run: sudo systemctl enable --now warp-svc"
        return 1
    fi
    $SUDO systemctl enable --now warp-svc >/dev/null 2>&1 \
        || $SUDO systemctl restart warp-svc >/dev/null 2>&1 || true
    local i
    for i in {1..30}; do
        warp_daemon_up && return 0
        sleep 0.5
    done
    return 1
}

warp_registered() {
    tmo 10 "$WARP_CLI" registration show >/dev/null 2>&1
}

warp_settings() { tmo 10 "$WARP_CLI" settings 2>/dev/null; }

warp_has_proxy_mode() { warp_settings | grep -q "WarpProxy"; }
warp_has_proxy_port() { warp_settings | grep -q "WarpProxy on port ${WARP_PORT}"; }

warp_prepare() {
    hdr "WARP"
    if [[ -z "$WARP_CLI" ]]; then
        bad "warp-cli not installed"
        info "install cloudflare-warp, then re-run this script"
        return 1
    fi
    ok "warp-cli    $WARP_CLI"

    if ! warp_daemon_start; then
        bad "warp-svc is not running"
        if have systemctl; then
            systemctl status warp-svc --no-pager -l 2>&1 | sed -n '1,12p' | sed 's/^/          /'
        fi
        info "try: sudo systemctl enable --now warp-svc"
        info "     sudo journalctl -u warp-svc -n 40 --no-pager"
        return 1
    fi
    ok "warp-svc    running"

    if ! warp_registered; then
        info "WARP is not registered; registering and accepting the ToS"
        if ! warp_tos registration new; then
            bad "WARP registration failed${WARP_LAST_ERR:+: $WARP_LAST_ERR}"
            return 1
        fi
        ok "WARP registered"
    else
        ok "WARP registered"
    fi

    if warp_has_proxy_mode && warp_has_proxy_port && port_listen "$WARP_PORT"; then
        if tmo 10 "$WARP_CLI" status 2>/dev/null | grep -qi "Connected"; then
            ok "proxy mode  ${WARP_PORT} (connected)"
            return 0
        fi
    fi

    info "configuring proxy mode on port ${WARP_PORT}"
    warp_run disconnect >/dev/null 2>&1 || true
    sleep 1

    if ! warp_has_proxy_mode; then
        warp_tos mode proxy || warp_tos set-mode proxy || true
    fi
    if ! warp_has_proxy_mode; then
        bad "WARP refused proxy mode${WARP_LAST_ERR:+: $WARP_LAST_ERR}"
        return 1
    fi
    ok "mode        proxy"

    if ! warp_has_proxy_port; then
        warp_tos proxy port "$WARP_PORT" || warp_tos set-proxy-port "$WARP_PORT" || true
    fi
    if ! warp_has_proxy_port; then
        bad "WARP refused proxy port ${WARP_PORT}${WARP_LAST_ERR:+: $WARP_LAST_ERR}"
        return 1
    fi
    ok "port        ${WARP_PORT}"

    # MASQUE is the preferred transport; WireGuard still works through the proxy.
    warp_tos tunnel protocol set MASQUE >/dev/null 2>&1 || true

    if ! tmo 10 "$WARP_CLI" status 2>/dev/null | grep -qi "Connected"; then
        info "connecting WARP"
        warp_tos connect || true
    fi

    local i
    for i in {1..60}; do
        port_listen "$WARP_PORT" && { ok "listening   127.0.0.1:${WARP_PORT}"; return 0; }
        sleep 0.5
    done

    local st set
    st="$(tmo 10 "$WARP_CLI" status 2>&1 | tr '\n' ' ' | cut -c1-200)"
    set="$(warp_settings | tr '\n' ' ' | cut -c1-200)"
    bad "WARP proxy port ${WARP_PORT} did not open"
    printf '          status:   %s\n' "${st:-unknown}"
    printf '          settings: %s\n' "${set:-unknown}"
    if printf '%s' "$st" | grep -qi "connecting"; then
        info "still connecting: this network may block WARP (UDP 2408/500/4500)"
    fi
    if have ss; then
        ss -ltnp 2>/dev/null | grep -E "[:.]${WARP_PORT}[[:space:]]" | sed 's/^/          holder: /' | head -3
    fi
    if have systemctl; then
        $SUDO journalctl -u warp-svc -n 12 --no-pager 2>/dev/null | tail -12 | sed 's/^/          svc: /'
    fi
    return 1
}

# =============================================================== PRE-FLIGHT ===
hdr "Pre-flight"
printf '  host        %s\n' "$(uname -srm)"
if [[ -r /etc/os-release ]]; then
    printf '  distro      %s\n' "$(sed -n 's/^PRETTY_NAME=//p' /etc/os-release | tr -d '"')"
else
    printf '  distro      %s\n' "unknown"
fi
printf '  date        %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
printf '  script sha  %s\n' "$(hash_file "$0")"

if [[ -z "$OC_BIN" ]]; then
    bad "opencode binary not found"
else
    ok "opencode    $OC_BIN ($(tmo 10 "$OC_BIN" --version 2>/dev/null | head -1))"
fi

ENV_JSON=""
ENV_PINNED=0
if [[ -n "$OC_BIN" ]]; then
    ENV_JSON="$(tmo 10 "$OC_BIN" service get env 2>/dev/null)"
    printf '%s' "$ENV_JSON" | grep -q "$PRIVOXY_PORT" && ENV_PINNED=1
    if [[ "$ENV_PINNED" -eq 1 ]]; then
        warn "service env is pinned to ${PROXY_URL}"
    else
        ok "service env not pinned"
    fi
fi

P8118=0; port_listen "$PRIVOXY_PORT" && P8118=1
P40000=0; port_listen "$WARP_PORT" && P40000=1
printf '  listeners   8118=%s 40000=%s\n' "$P8118" "$P40000"

if [[ -n "$WARP_CLI" ]]; then
    WSTAT="$(tmo 10 "$WARP_CLI" status 2>/dev/null | tr '\n' ' ' | cut -c1-100)"
    WSET="$(warp_settings | grep -m1 '^Mode:' || true)"
    WDAEMON="$(systemctl is-active warp-svc 2>/dev/null || true)"
    ok "warp-cli    $WARP_CLI"
    printf '  warp daemon %s\n' "${WDAEMON:-unknown}"
    printf '  warp        %s%s\n' "${WSTAT:-unreachable}" "${WSET:+  [$WSET]}"
else
    warn "warp-cli not installed"
fi

if have privoxy; then ok "privoxy     $(command -v privoxy)"; else warn "privoxy not installed"; fi

P_TRACE="$(trace_proxy)"
P_WARP="$(printf '%s' "$P_TRACE" | field warp)"
P_IP="$(printf '%s' "$P_TRACE" | field ip)"
if [[ -n "$P_IP" ]]; then
    printf '  proxy egress %s warp=%s\n' "$P_IP" "${P_WARP:-?}"
else
    info "no egress through 8118"
fi

INSTALLED_HASH=""
[[ -f "$BIN_TARGET" ]] && INSTALLED_HASH="$(hash_file "$BIN_TARGET")"
PLUGIN_HASH=""
[[ -f "$PLUGIN" ]] && PLUGIN_HASH="$(hash_file "$PLUGIN")"
printf '  proxy build  %s%s\n' "${INSTALLED_HASH:0:16}…" "$([[ "$INSTALLED_HASH" == "$HASH_PROXY" ]] && echo ' (current)' || echo ' (stale/missing)')"
printf '  plugin build %s%s\n' "${PLUGIN_HASH:0:16}…" "$([[ "$PLUGIN_HASH" == "$HASH_PLUGIN" ]] && echo ' (current)' || echo ' (stale/missing)')"

if [[ "$MODE" == "check" ]]; then
    hdr "State"
    if [[ "$ENV_PINNED" -eq 1 && "$P8118" -eq 0 ]]; then
        bad "phantom proxy: env pinned to 8118, nothing listening -> every model fails"
    elif [[ "$ENV_PINNED" -eq 1 && "$P_WARP" != "on" ]]; then
        bad "dead forward: 8118 up but not egressing through WARP"
    elif [[ "$ENV_PINNED" -eq 1 ]]; then
        ok "proxy ON and routing through WARP"
    else
        ok "proxy OFF, direct connection"
    fi
    [[ -f "$UNIT_DIR/opencode-proxy-guard.timer" ]] && ok "guard timer present" || warn "no guard timer"
    if [[ -n "$WARP_CLI" ]]; then
        [[ "${WDAEMON:-}" == "active" ]] && ok "warp-svc active" || bad "warp-svc inactive — WARP proxy cannot start"
        if warp_has_proxy_port; then
            [[ "$P40000" -eq 1 ]] && ok "WARP proxy listening on ${WARP_PORT}" || bad "WARP configured for ${WARP_PORT} but the port is closed (not connected?)"
        else
            warn "WARP is not in proxy mode on ${WARP_PORT}"
        fi
    fi
    exit 0
fi

PROXY_B64='
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
'
PLUGIN_B64='
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
'

# ---------------------------------------------------------------- enable/reset
proxy_healthy() {
    port_listen "$PRIVOXY_PORT" || return 1
    [[ "$(trace_proxy | field warp)" == "on" ]] || return 1
    return 0
}

clear_env() {
    [[ -n "$OC_BIN" ]] || return 0
    for v in HTTPS_PROXY HTTP_PROXY ALL_PROXY NO_PROXY; do
        tmo 10 "$OC_BIN" service unset env "$v" >/dev/null 2>&1 || true
    done
    tmo 20 "$OC_BIN" service restart >/dev/null 2>&1 || true
}

enable_proxy() {
    [[ -n "$WARP_CLI" ]] || die "warp-cli missing — OpenCode still works direct"
    if ! warp_prepare; then
        clear_env
        die "WARP is not ready; service env cleared, OpenCode still works direct"
    fi
    if "$BIN_TARGET" guard >/dev/null 2>&1; then
        ok "guard: WARP proxy mode + privoxy healthy"
    else
        warn "guard could not confirm health; 'opencode-proxy on' will decide"
    fi
    if "$BIN_TARGET" on; then
        ok "proxy enabled"
    else
        die "opencode-proxy on failed — service env is clear, OpenCode still works direct"
    fi
}

safe_reset() {
    hdr "Safe reset"
    info "guard first: a reset must never pin env before WARP+privoxy work"
    "$BIN_TARGET" guard >/dev/null 2>&1 || true
    if ! proxy_healthy; then
        clear_env
        bad "proxy is not healthy; refusing to reset"
        info "env cleared and service restarted — the machine is back to direct mode"
        exit 1
    fi
    ok "proxy healthy: 8118 up and egressing through WARP"

    if ! have sqlite3; then
        warn "sqlite3 missing; DB banner cleanup will be skipped"
    fi

    warn "reset probes with real model calls (up to 8 messages)"
    if ! confirm "Run the quota-rotating reset now?"; then
        info "skipped"
        exit 0
    fi

    if "$BIN_TARGET" reset; then
        if proxy_healthy && tmo 10 "$OC_BIN" service get env 2>/dev/null | grep -q "$PRIVOXY_PORT"; then
            ok "reset complete and consistent"
        else
            warn "reset finished but state is inconsistent; clearing env"
            clear_env
            exit 1
        fi
    else
        bad "reset failed"
        clear_env
        info "env cleared so no provider is left pinned to a dead proxy"
        exit 1
    fi
}

# =================================================================== INSTALL ===
hdr "Update"
printf '  target      %s\n' "$BIN_TARGET"
printf '  plugin      %s\n' "$PLUGIN"
printf '  proxy sha   %s\n' "$HASH_PROXY"
printf '  plugin sha  %s\n' "$HASH_PLUGIN"

if [[ "$DEPS" != "no" ]]; then
    MISSING=""
    have privoxy || MISSING="$MISSING privoxy"
    have lsof || MISSING="$MISSING lsof"
    have sqlite3 || MISSING="$MISSING sqlite"
    have gzip || MISSING="$MISSING gzip"
    have curl || MISSING="$MISSING curl"
    if [[ -n "$MISSING" ]]; then
        if [[ -z "$SUDO" && "$(id -u)" -ne 0 ]]; then
            warn "cannot install automatically (no sudo). Run: sudo dnf install -y$MISSING"
        elif confirm "Install packages:$MISSING ?"; then
            $SUDO dnf install -y $MISSING >/dev/null 2>&1 && ok "installed$MISSING" || warn "dnf failed for$MISSING"
        fi
    else
        ok "packages present"
    fi

    if [[ -z "$WARP_CLI" ]]; then
        info "Cloudflare WARP is not installed"
        if [[ -z "$SUDO" && "$(id -u)" -ne 0 ]]; then
            warn "install manually: see https://pkg.cloudflareclient.com"
        elif confirm "Add the Cloudflare repo and install cloudflare-warp?"; then
            $SUDO rpm --import https://pkg.cloudflareclient.com/pubkey.gpg >/dev/null 2>&1
            printf '[cloudflare-warp]\nname=cloudflare-warp\nbaseurl=https://pkg.cloudflareclient.com/\nenabled=1\ngpgcheck=1\ngpgkey=https://pkg.cloudflareclient.com/pubkey.gpg\n' \
                | $SUDO tee /etc/yum.repos.d/cloudflare-warp.repo >/dev/null 2>&1
            $SUDO dnf install -y cloudflare-warp >/dev/null 2>&1 && ok "cloudflare-warp installed" || warn "cloudflare-warp install failed"
            $SUDO systemctl enable --now warp-svc >/dev/null 2>&1 || true
            WARP_CLI="$(warp_bin)"
        fi
    fi
fi

if [[ "$MODE" == "install" ]]; then
    # Make WARP usable now and at boot. A reset can never pin env safely
    # while the WARP SOCKS port is missing.
    warp_prepare || warn "WARP is not ready; proxy stays off and OpenCode stays direct"
fi

# Keep the old build and the old plugin, one each.
BK="$HOME/.local/state/owp-fedora/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK"
[[ -f "$BIN_TARGET" ]] && cp -p "$BIN_TARGET" "$BK/opencode-proxy.old" 2>/dev/null
[[ -f "$PLUGIN" ]] && cp -p "$PLUGIN" "$BK/privacy-shield.js.old" 2>/dev/null
[[ -f "$PRIVOXY_CONF" ]] && cp -p "$PRIVOXY_CONF" "$BK/" 2>/dev/null
[[ -n "$OC_BIN" ]] && tmo 10 "$OC_BIN" service get env > "$BK/service-env.json" 2>/dev/null
ok "backup      $BK"

TMPD="$(mktemp -d "${TMPDIR:-/tmp}/owp-fedora.XXXXXX")"
trap 'rm -rf "$TMPD"' EXIT
decode_fail=0
printf '%s' "$PROXY_B64" | base64 -d 2>/dev/null | gzip -dc > "$TMPD/opencode-proxy" 2>/dev/null || decode_fail=1
printf '%s' "$PLUGIN_B64" | base64 -d 2>/dev/null | gzip -dc > "$TMPD/privacy-shield.js" 2>/dev/null || decode_fail=1
[[ "$decode_fail" -eq 1 ]] && die "payload decode failed (need base64 + gzip)"

for pair in "opencode-proxy:$HASH_PROXY" "privacy-shield.js:$HASH_PLUGIN"; do
    f="${pair%%:*}"; want="${pair##*:}"
    got="$(hash_file "$TMPD/$f")"
    [[ "$got" == "$want" ]] && ok "verified $f" || die "$f hash mismatch"
done

mkdir -p "$HOME/.local/bin" "$HOME/.opencode/bin" "$(dirname "$PLUGIN")"
install -m 755 "$TMPD/opencode-proxy" "$BIN_TARGET" && ok "installed proxy" || die "install failed"
install -m 644 "$TMPD/privacy-shield.js" "$PLUGIN" && ok "installed plugin" || die "install failed"
ln -sfn "$BIN_TARGET" "$BIN_LINK" && ok "linked $BIN_LINK"

# One copy only; the retired loop plugin is removed.
for stale in "$HOME/.opencode/plugins/privacy-shield.js" \
             "$CONFIG_DIR/plugins/auto-resume.js" \
             "$HOME/.opencode/plugins/auto-resume.js"; do
    [[ -f "$stale" ]] && rm -f "$stale" && ok "removed $stale"
done

# A previous install can leave proxy vars pinned with nothing listening.
# That is the failure that makes every model fail, so clear it here.
hdr "Service env"
if [[ "$ENV_PINNED" -eq 1 ]]; then
    info "clearing proxy vars pinned by a previous install"
    clear_env
    AFTER_ENV="$(tmo 10 "$OC_BIN" service get env 2>/dev/null)"
    if printf '%s' "$AFTER_ENV" | grep -q "$PRIVOXY_PORT"; then
        warn "service env still pinned after unset; inspect: $OC_BIN service get env"
    else
        ok "service env cleared"
    fi
else
    ok "service env already clean"
fi

hdr "Guard"
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
    systemctl --user enable --now opencode-proxy-guard.timer >/dev/null 2>&1 && ok "timer enabled" || warn "could not enable timer"
    loginctl enable-linger "$(id -un)" >/dev/null 2>&1 && ok "linger enabled" || info "linger not enabled"
else
    warn "no systemd user manager; add cron instead:"
    printf '          */15 * * * * %s guard >/dev/null 2>&1\n' "$BIN_TARGET"
fi

case "$MODE" in
    install)
        hdr "Done"
        info "proxy left OFF. Enable with: $BIN_TARGET on"
        ;;
    on)
        enable_proxy
        ;;
    reset)
        enable_proxy
        safe_reset
        ;;
esac

hdr "Final"
F_P=0; port_listen "$PRIVOXY_PORT" && F_P=1
F_E=0
[[ -n "$OC_BIN" ]] && tmo 10 "$OC_BIN" service get env 2>/dev/null | grep -q "$PRIVOXY_PORT" && F_E=1
F_W="$(trace_proxy | field warp)"
printf '  8118=%s env_pinned=%s proxy_warp=%s\n' "$F_P" "$F_E" "${F_W:-?}"
if [[ "$F_E" -eq 1 && "$F_P" -eq 0 ]]; then
    bad "env pinned to a dead proxy"; exit 1
elif [[ "$F_E" -eq 1 && "$F_W" != "on" ]]; then
    bad "env pinned but egress is not WARP"; exit 1
elif [[ "$F_E" -eq 1 ]]; then
    ok "proxy ON and routing through WARP"
else
    ok "direct mode — every provider works"
fi
exit 0
