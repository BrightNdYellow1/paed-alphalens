FROM python:3.12-slim
WORKDIR /app
COPY sde-lab/azure/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY alphalens/__init__.py alphalens/sde_demo.py alphalens/sde_job.py /app/alphalens/
USER 65532
ENTRYPOINT ["python", "-m", "alphalens.sde_job"]
