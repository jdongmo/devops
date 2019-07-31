# Devops
Ansible repository to perform automatic tasks for devops team.

## Requirements

To run AWS recipe, you should have AWS variable (credentials and region) set in environment
or having vault file with these variables:
- aws_access_key
- aws_secret_key

## Run
To run a playbook, we'll use wrapper script run.sh
To run default infrastructure playbook *infra.yml* who create all the infra
```
./run.sh -v
```
To run another playbook *playbook.yml* after default playbook
```
./run.sh -v playbook.yml
```
To only play another playbook *playbook.yml*
```
ANSIBLE_PLAYBOOK_FILE=playbook.yml ./run.sh -v
```
To only play another playbook (playbook.yml) against specific host *host*
```
ANSIBLE_PLAYBOOK_FILE=playbook.yml ./run.sh -v --limit host
```

## Docker
We have a Dockerfile in order to generate a docker image to use it for
running play in an controled environment.
- Build image: ```docker build -t devops-docker .```
- Run a play using this image:
```
docker run -e "AWS_REGION=$AWS_REGION" -e "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" \
-e "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" --entrypoint "./run.sh"
devops-docker -v --linit host
```
