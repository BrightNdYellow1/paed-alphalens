# Run the synthetic vaccination pipeline in Azure

This lab uses a private Blob container and a Container Apps job. It processes
fabricated fixtures only. The container image contains the application, not
the data or any credentials. An existing Azure subscription, Container Apps
environment, Blob container and accessible container registry are required.
Review the cost of those resources before creating them.

## Package and configure the job

Build the image from the repository root with
`docker build -f sde-lab/azure/Dockerfile -t "$IMAGE" .` and push it to a
registry the job can pull from. For a private registry, use an approved
registry pull identity and grant pull access. Set these values in Azure CLI
using the resource names for your lab:

```bash
RG=rg-alphalens-demo
ACCOUNT=your_storage_account_name
CONTAINER=alphalens
ENVIRONMENT=your_container_apps_environment
JOB=alphalens-vaccination
IMAGE=your_registry/alphalens-sde:demo
```

Upload each input version completely before starting a job. Keep its blob
names and contents fixed so a manifest can be traced to a stable set of
inputs. This example uses the signed-in CLI identity for uploading fixtures.

```bash
for file in cohort.csv practice.csv external.csv; do
  az storage blob upload --account-name "$ACCOUNT" --container-name "$CONTAINER" \
    --auth-mode login --name "inputs/valid/$file" --file "sde-lab/fixtures/$file"
done
```

For an image that can be pulled without registry authentication, create the
job as follows. For private images, also supply the registry identity settings
for your environment.

```bash
az containerapp job create --name "$JOB" --resource-group "$RG" \
  --environment "$ENVIRONMENT" --trigger-type Manual --mi-system-assigned \
  --cpu 0.25 --memory 0.5Gi --replica-timeout 180 --replica-retry-limit 0 \
  --image "$IMAGE" \
  --env-vars "SDE_ACCOUNT_URL=https://$ACCOUNT.blob.core.windows.net" \
    "SDE_CONTAINER=$CONTAINER" SDE_INPUT_VERSION=valid
```

Assign the job's system-assigned managed identity **Storage Blob Data
Contributor** scoped to the lab container. The job uses its managed identity
for Blob requests. Give researchers access only to approved aggregated
outputs through a separate governed publication path in a real implementation.
Using one container and one job identity is for this synthetic exercise.

```bash
az containerapp job start --name "$JOB" --resource-group "$RG"
az containerapp job execution list --name "$JOB" --resource-group "$RG" -o table
```

## Failure and recovery drill

1. Save the successful execution record and the files under its unique
   `runs/<run-id>/` prefix. Treat a report as published only if that prefix
   also contains a completed manifest. Compare the report SHA-256 with the
   value in the manifest.
2. Upload a separate `inputs/duplicate/` version. Use copies of the same
   three files but append an existing synthetic ID to the cohort CSV. Change
   `SDE_INPUT_VERSION` on the job to `duplicate` and start it again.
3. Confirm that the execution fails with a validation rejection and writes
   `failure.json` without a completion manifest. Check that the original
   successful report is still available and its checksum is unchanged. If
   permissions prevent writing failure evidence, inspect the execution logs.
4. Upload a `corrected` version with the duplicate removed. Run against that
   version, reconcile the six cohort members and check the new report hash.
5. After the drill, create a separate scheduled job using the same image and
   environment settings, with `--trigger-type Schedule --cron-expression
   '15 8 * * 1'` in place of the manual trigger. Assign the scheduled job
   identity its own container access. Cron is in UTC. Enable it only while
   you want the lab to run.

Each completion manifest records duration, input bytes and report bytes.
These are workload observations, not Azure billing measurements. Use Azure
Cost Management for actual charges and a lifecycle policy for retained test
inputs and outputs. Verify the complete run on Azure before making a live
deployment claim.

Microsoft reference: https://learn.microsoft.com/azure/container-apps/jobs-get-started-cli
