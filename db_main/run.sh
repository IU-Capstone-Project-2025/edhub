#!/bin/bash
echo test
if [ -z "$(ls $PGDATA)" ]; then
    initdb
    rm $PGDATA/pg_hba.conf
    cp scripts/pg_hba.conf $PGDATA
    pg_ctl -D "$PGDATA" start
    psql -f scripts/initialize.sql
else
    pg_ctl -D "$PGDATA" start
fi
trap 'echo exiting' INT
sleep INFINITY &
wait $!
pg_ctl -D "$PGDATA" stop
