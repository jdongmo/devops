#!/usr/bin/env bash

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
export VAULT_PASSWORD_FILE="${VAULT_PASSWORD_FILE:-${HOME}/.ssh/creds/vault_password.txt}"
export VAGRANT_MODE="${VAGRANT_MODE:-0}"

# Fix for strange mounting issues. Should find a better solution.
if [ -d "/root/ssh" ];then cp -R /root/ssh /root/.ssh; fi
if [ -d "/root/devops" ];then cp -R /root/devops/* /opt/devops; fi

run_ansible() {
  INOPTS=( "$@" )
  VAULTOPTS=""
  # Plaintext vault decryption key, not checked into SCM
  if [ -f "${VAULT_PASSWORD_FILE}" ]; then
    VAULTOPTS="--vault-password-file=${VAULT_PASSWORD_FILE}"
    if [ ${ANSIBLE_RUN_MODE} == 'playbook' ]; then
      time ansible-playbook --diff "${VAULTOPTS}" "${ANSIBLE_PLAYBOOK_FILE}" "${INOPTS[@]}"
      return $?
    elif [ ${ANSIBLE_RUN_MODE} == 'ad-hoc' ]; then
      time ansible --diff "${VAULTOPTS}" "${INOPTS[@]}"
      return $?
    fi
  else
    if [ "${ANSIBLE_RUN_MODE}" == 'playbook' ]; then
      echo "Vault password file unreachable. Skip steps require vault."
      VAULTOPTS="--skip-tags=requires_vault"
      #echo "ansible-playbook --diff $VAULTOPTS ${INOPTS[@]} ${ANSIBLE_PLAYBOOK_FILE}" && \
      time ansible-playbook --diff "${VAULTOPTS}" "${ANSIBLE_PLAYBOOK_FILE}" "${INOPTS[@]}"
      return $?
    elif [ "${ANSIBLE_RUN_MODE}" == 'ad-hoc' ]; then
      #echo "ansible --diff $VAULTOPTS ${INOPTS[@]}" && \
      time ansible --diff "${VAULTOPTS}" "${INOPTS[@]}"
      return $?
    else
      echo "Invalid run mode: ${ANSIBLE_RUN_MODE}"
      exit 15
    fi
  fi
}

if [ "${VAGRANT_MODE}" -eq 1 ]; then
  export ANSIBLE_SSH_ARGS="-o UserKnownHostsFile=/dev/null"
  export ANSIBLE_HOST_KEY_CHECKING=false
fi

run_ansible "$@"
retcode=$?
exit $retcode
