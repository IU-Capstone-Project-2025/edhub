FROM postgres
WORKDIR /
RUN mkdir scripts
COPY initialize.sql ../run.sh ../pg_hba.conf scripts/
USER postgres
ENTRYPOINT ["bash", "scripts/run.sh"]
