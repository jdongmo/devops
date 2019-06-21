#!/usr/bin/env ash

# ENV Vars:
#   VAGRANT_MODE - [0,1] 
#     - to be used with bovine-inventory's vagrant mode
#   ANSIBLE_RUN_MODE - ["playbook","ad-hoc"]
#     - specify which mode to run ansible in
#   ANSIBLE_PLAYBOOK_FILE - defaults to "infra.yml"
#     - specify playbook to pass to ansible-playbook
#     - NB: only used when run mode is "playbook"
#   ANSIBLE_BASE_ARA - ["0","1"]
#     - a bash STRING (not numeral) to enable ARA
#   VAULT_PASSWORD_FILE - 

export ANSIBLE_RUN_MODE="${ANSIBLE_RUN_MODE:-playbook}"
export ANSIBLE_PLAYBOOK_FILE="${ANSIBLE_PLAYBOOK_FILE:-infra.yml}"
export VAULT_PASSWORD_FILE="${VAULT_PASSWORD_FILE:-./creds/vault_password.txt}"
export VAGRANT_MODE="${VAGRANT_MODE:-0}"

run_ansible() {
  INOPTS=("$@")
  VAULTOPTS=""
  # Plaintext vault decryption key, not checked into SCM
  if [[ -f ${VAULT_PASSWORD_FILE} ]]; then
    VAULTOPTS="--vault-password-file=${VAULT_PASSWORD_FILE}"
    [[ ${ANSIBLE_RUN_MODE} == 'playbook' ]] && \
      ansible-playbook --diff "${ANSIBLE_PLAYBOOK_FILE}" $VAULTOPTS "${INOPTS[@]}"
    [[ ${ANSIBLE_RUN_MODE} == 'ad-hoc' ]] && \
      ansible --diff "${INOPTS[@]}" $VAULTOPTS
  else
    if [[ ${ANSIBLE_RUN_MODE} == 'playbook' ]]; then
      echo "Vault password file unreachable. Skip steps require vault."
      VAULTOPTS="--skip-tags requires_vault"
      ansible-playbook --diff "${ANSIBLE_PLAYBOOK_FILE}" $VAULTOPTS "${INOPTS[@]}"
    elif [[ ${ANSIBLE_RUN_MODE} == 'ad-hoc' ]]; then
      ansible --diff "${INOPTS[@]}" $VAULTOPTS
    else
      echo "Invalid run mode: ${ANSIBLE_RUN_MODE}"
      exit 15
    fi
  fi
}

if [ $# -eq 0 ]; then
  echo "No arguments provided, please provide at least one argument"
  echo "Example: ./run.sh -v"
  exit 1
fi

if [[ ${VAGRANT_MODE} == 1 ]]; then
  export ANSIBLE_SSH_ARGS="-o UserKnownHostsFile=/dev/null"
  export ANSIBLE_HOST_KEY_CHECKING=false
fi

time run_ansible "${@}"
retcode=$?
exit $retcode
