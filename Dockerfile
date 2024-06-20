FROM python:3.10

COPY ${PWD} /PCC-CAS
WORKDIR /PCC-CAS/
RUN pip install -r req.txt
RUN chmod +rx startup.sh
CMD ["./startup.sh"]
