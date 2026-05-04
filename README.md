# sample-app

A minimal Python Flask service wired into a full **GitHub Actions → JFrog → Harness → Kubernetes** delivery pipeline.

## Flow

```
git push  ─▶  GitHub Actions  ─▶  JFrog Artifactory + Xray  ─▶  Harness  ─▶  Kubernetes
              (test, build)        (store, scan)                 (Dev → QA → Prod)
```

## Layout

| Path | Purpose |
|---|---|
| `app/` | Flask application code |
| `tests/` | Pytest unit tests |
| `Dockerfile` | Container image definition |
| `k8s/` | Kubernetes manifests (consumed by Harness) |
| `.github/workflows/ci.yml` | CI: test → build → push → scan → trigger CD |
| `.harness/sample_app_deploy.yaml` | Harness CD pipeline (Dev → QA canary → Prod blue-green) |

## Run locally

```powershell
cd sample-app
docker build -t sample-app:local .
docker run --rm -p 8080:8080 sample-app:local
# In another shell
curl http://localhost:8080/health
```

## Required GitHub configuration

### Repository Variables  (`Settings → Secrets and variables → Actions → Variables`)
| Name | Example |
|---|---|
| `JFROG_URL` | `https://mycorp.jfrog.io` |
| `HARNESS_ACCOUNT_ID` | `abc123` |
| `HARNESS_ORG_ID` | `default` |
| `HARNESS_PROJECT_ID` | `platform` |

### Repository Secrets
| Name | Notes |
|---|---|
| `HARNESS_API_KEY` | Harness service-account API key |

## Required JFrog configuration

1. Create a Docker repository: `docker-sample-local`.
2. Configure **OIDC** for GitHub Actions (Administration → Manage Integrations → OIDC):
   - Provider name: `github-jfrog-oidc`
   - Issuer: `https://token.actions.githubusercontent.com`
   - Map identity mapping → user with push permission.
3. Create an **Xray Watch** on `docker-sample-local` (e.g. fail on CVSS ≥ 7).

## Required Harness configuration

1. **Kubernetes connector** (delegate-based) for each environment (dev/qa/prod).
2. **Artifactory connector** to JFrog.
3. Import `.harness/sample_app_deploy.yaml` (replace `<YOUR_ORG_ID>` / `<YOUR_PROJECT_ID>`).
4. Create environments `dev`, `qa`, `prod` and infra defs `dev_k8s`, `qa_k8s`, `prod_k8s`.
5. Create a Harness **Service** named `sample_app_service` referencing the K8s manifests in `k8s/` and the Artifactory image `sample-app`.

## What the workflow does

1. **test** — Installs deps, runs `pytest`.
2. **build-publish** — Builds Docker image, pushes to JFrog, publishes build info, runs Xray scan (fails on policy violation).
3. **trigger-harness** — Calls Harness REST API with the new `image_tag` to start the deployment pipeline.
