#!/bin/bash

RESULTS="/tmp/results"
LOG="${RESULTS}/output.log"

curl "{{ site_url }}{% url "start_run" run.secret_key %}"
mkdir -p $RESULTS

(
    set -x
    {% for param in run.params %}
    export {{ param.box_param.name|upper }}="{{ param.value }}"
    {% endfor %}
    {% autoescape off %}
    {{ run.box.get_sources }}
    cd {{ vm_src }}
    {{ run.box.before_run }}
    {{ run.box.run_command }}
    RET_CODE=$?
    {{ run.box.after_run }}
    {% endautoescape %}
    [ $RET_CODE -eq 0 ] && /bin/true || /bin/false
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
