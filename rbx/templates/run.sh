#!/bin/bash

RESULTS="/tmp/$(uuidgen)"
RUN_DIR="/tmp/$(uuidgen)"

LOG="${RESULTS}/output.log"

curl "{{ site_url }}{% url "start_run" run.secret_key %}"
mkdir -p $RESULTS
mkdir -p $RUN_DIR

rbx_auto_config() {
    if [ "x$(ls | grep -i Makefile)" != "x" ]; then
        make
        for exec in $(find . -type f -perm +111 -d 1 -print); do
            $exec
        done
    else
        echo "Unable to configure projet :("
    fi
}

(
    set -x
    {% for param in run.params %}
    export {{ param.box_param.name|upper }}="{{ param.value }}"
    {% endfor %}
    {% autoescape off %}
    cd $RUN_DIR
    {{ run.box.get_sources }}
    cd {{ vm_src }}
    {{ run.box.command }}
    RET_CODE=$?
    {% endautoescape %}
    [ $RET_CODE -eq 0 ] && true || false
) > $LOG 2>&1

RET_CODE=$?

cd $RESULTS
for FILE in $(ls $RESULTS); do
    curl -F file=@${RESULTS}/${FILE} -F title=${FILE} "{{ site_url }}{% url "save_data" run.secret_key %}"
done

if [ $RET_CODE -eq 0 ]; then
    curl "{{ site_url }}{% url "run_succeeded" run.secret_key %}"
else
    curl "{{ site_url }}{% url "run_failed" run.secret_key %}"
fi
