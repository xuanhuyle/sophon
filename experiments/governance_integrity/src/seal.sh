#!/usr/bin/env bash
# Seal / unseal answer-bearing material around solver runs (PROTOCOL.md §7).
#
#   src/seal.sh seal   KEYFILE  PATH...   # tar + AES-256-CBC (pbkdf2) each PATH into PATH.sealed.tar.enc, then remove the plaintext
#   src/seal.sh unseal KEYFILE  PATH...   # decrypt PATH.sealed.tar.enc back into place, then remove the archive
#
# KEYFILE holds the passphrase (random bytes, created by the orchestrator outside every solver
# directory). The protection is against accidental access and search by solver agents that share
# the OS user; it is not a defence against a deliberately adversarial process with the same user.
set -euo pipefail
mode="$1"; key="$2"; shift 2
for p in "$@"; do
  case "$mode" in
    seal)
      [ -e "$p" ] || { echo "skip (absent): $p"; continue; }
      parent=$(dirname "$p"); base=$(basename "$p")
      tar -C "$parent" -cf - "$base" | openssl enc -aes-256-cbc -pbkdf2 -salt -pass "file:$key" -out "$p.sealed.tar.enc"
      rm -rf "$p"
      echo "sealed: $p -> $p.sealed.tar.enc ($(stat -c %s "$p.sealed.tar.enc") bytes)"
      ;;
    unseal)
      [ -e "$p.sealed.tar.enc" ] || { echo "skip (no archive): $p"; continue; }
      parent=$(dirname "$p")
      openssl enc -d -aes-256-cbc -pbkdf2 -pass "file:$key" -in "$p.sealed.tar.enc" | tar -C "$parent" -xf -
      rm -f "$p.sealed.tar.enc"
      echo "unsealed: $p"
      ;;
    *) echo "usage: seal.sh seal|unseal KEYFILE PATH..." >&2; exit 2;;
  esac
done
