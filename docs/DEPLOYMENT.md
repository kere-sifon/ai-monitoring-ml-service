# Deployment Guide

This guide covers deploying the ML Service to both Azure Kubernetes Service (AKS) and OpenShift.

## Table of Contents

- [Prerequisites](#prerequisites)
- [AKS Deployment](#aks-deployment)
- [OpenShift Deployment](#openshift-deployment)
- [PR Comment-Based Deployment](#pr-comment-based-deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Common Requirements

- Docker or Podman
- Helm 3.13+
- kubectl or oc CLI
- Access to container registry (GitHub Container Registry)

### AKS-Specific

- Azure CLI (`az`)
- Azure subscription with AKS cluster
- Appropriate RBAC permissions

### OpenShift-Specific

- OpenShift CLI (`oc`)
- OpenShift cluster access
- Project creation permissions

## AKS Deployment

### Manual Deployment

1. **Login to Azure and get AKS credentials:**

```bash
az login
az aks get-credentials \
  --resource-group <your-resource-group> \
  --name <your-cluster-name>
```

2. **Verify connection:**

```bash
kubectl cluster-info
kubectl get nodes
```

3. **Deploy with Helm:**

```bash
helm upgrade --install ml-service ./charts \
  --namespace ai-monitoring \
  --create-namespace \
  -f charts/values.yaml \
  --set image.tag=1.0.1
```

4. **Verify deployment:**

```bash
kubectl get pods -n ai-monitoring
kubectl get svc -n ai-monitoring
kubectl get hpa -n ai-monitoring
```

### Automated Deployment

**Via Main Branch:**
- Push to `main` branch triggers automatic deployment to AKS
- Uses the image tag specified in `charts/values.yaml`

**Via PR Comment:**
- Comment `/deploy aks` on any open PR
- Deploys the PR's code to AKS for testing
- Requires write access to the repository

## OpenShift Deployment

### Manual Deployment

1. **Login to OpenShift:**

```bash
oc login --token=<your-token> --server=<your-server-url>
```

2. **Create or switch to project:**

```bash
oc new-project ai-monitoring
# or
oc project ai-monitoring
```

3. **Deploy with Helm:**

```bash
helm upgrade --install ml-service ./charts \
  --namespace ai-monitoring \
  --create-namespace \
  -f charts/values.yaml \
  -f charts/values-openshift.yaml \
  --set image.tag=1.0.1
```

4. **Verify deployment:**

```bash
oc get pods -n ai-monitoring
oc get svc -n ai-monitoring
oc get route -n ai-monitoring
```

5. **Get the Route URL:**

```bash
oc get route ml-service -n ai-monitoring -o jsonpath='{.spec.host}'
```

### Automated Deployment

**Via PR Comment:**
- Comment `/deploy openshift` or `/deploy oc` on any open PR
- Deploys the PR's code to OpenShift for testing
- Requires write access to the repository
- Automatically creates an OpenShift Route

## PR Comment-Based Deployment

### How It Works

1. Open a pull request with your changes
2. Wait for tests to pass (optional but recommended)
3. Add a comment to the PR:
   - `/deploy aks` - Deploy to Azure Kubernetes Service
   - `/deploy openshift` or `/deploy oc` - Deploy to OpenShift

4. The GitHub Actions workflow will:
   - Verify you have write access
   - Build the Docker image with the PR's commit SHA
   - Deploy to the specified platform
   - Comment back with deployment status and details

### Requirements

- **Repository Access**: You must have write access to trigger deployments
- **Open PR**: The PR must be open (not closed or merged)
- **Secrets Configured**: Required secrets must be set in GitHub repository settings

### Example Comments

```
/deploy aks
```

```
/deploy openshift
```

```
/deploy oc
```

### Deployment Feedback

The workflow will add reactions and comments to your PR:

- 🚀 Rocket reaction: Deployment started
- ✅ Success comment: Deployment completed with details
- ❌ Failure comment: Deployment failed with link to logs

## Configuration

### GitHub Secrets

Configure these secrets in your GitHub repository settings (Settings → Secrets and variables → Actions):

#### For AKS Deployments

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AZURE_CREDENTIALS` | Azure service principal JSON | `{"clientId":"...","clientSecret":"...","subscriptionId":"...","tenantId":"..."}` |
| `AKS_RESOURCE_GROUP` | Azure resource group name | `my-resource-group` |
| `AKS_CLUSTER_NAME` | AKS cluster name | `my-aks-cluster` |

#### For OpenShift Deployments

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `OPENSHIFT_TOKEN` | OpenShift authentication token | `sha256~abc123...` |
| `OPENSHIFT_SERVER` | OpenShift API server URL | `https://api.cluster.example.com:6443` |
| `OPENSHIFT_PROJECT` | OpenShift project/namespace | `ai-monitoring` |

### Helm Values

#### Common Values (`charts/values.yaml`)

```yaml
replicaCount: 1

image:
  repository: ghcr.io/keresifon/ai-monitoring-ml-service
  tag: "1.0.1"

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 2
  targetCPUUtilizationPercentage: 70
```

#### OpenShift-Specific Values (`charts/values-openshift.yaml`)

```yaml
openshift:
  enabled: true
  route:
    enabled: true
    tls:
      enabled: true
      termination: edge
```

### Environment Variables

Configure these in `charts/values.yaml`:

```yaml
env:
  MODEL_PATH: /app/models
  LOG_LEVEL: INFO
  MODEL_TYPE: isolation-forest
```

## Troubleshooting

### Common Issues

#### 1. Deployment Fails with "Model not loaded"

**Solution:** The service starts without a trained model. Train a model using the API:

```bash
curl -X POST http://<service-url>/api/v1/train \
  -H "Content-Type: application/json" \
  -d @sample_training_data.json
```

#### 2. Pod CrashLoopBackOff

**Check logs:**
```bash
# AKS
kubectl logs -n ai-monitoring -l app.kubernetes.io/name=ml-service

# OpenShift
oc logs -n ai-monitoring -l app.kubernetes.io/name=ml-service
```

**Common causes:**
- Insufficient resources
- Image pull errors
- Configuration errors

#### 3. OpenShift Route Not Accessible

**Check route status:**
```bash
oc get route ml-service -n ai-monitoring
oc describe route ml-service -n ai-monitoring
```

**Verify TLS configuration:**
```bash
curl -v https://<route-url>/api/v1/health
```

#### 4. PR Comment Deployment Not Triggering

**Verify:**
- You have write access to the repository
- The comment is on a pull request (not an issue)
- The comment starts with `/deploy` followed by `aks`, `openshift`, or `oc`
- Required secrets are configured

#### 5. Image Pull Errors

**For private registries:**

```bash
# Create image pull secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n ai-monitoring

# Update values.yaml
imagePullSecrets:
  - name: ghcr-secret
```

### Getting Help

1. **Check workflow logs**: Go to Actions tab in GitHub
2. **Check pod logs**: Use `kubectl logs` or `oc logs`
3. **Check events**: Use `kubectl get events` or `oc get events`
4. **Describe resources**: Use `kubectl describe` or `oc describe`

### Health Checks

**Health endpoint:**
```bash
curl http://<service-url>/api/v1/health
```

**Readiness endpoint:**
```bash
curl http://<service-url>/api/v1/ready
```

**Model info:**
```bash
curl http://<service-url>/api/v1/model/info
```

## Best Practices

1. **Use PR deployments for testing**: Test changes in isolation before merging
2. **Monitor resource usage**: Check HPA metrics and adjust limits if needed
3. **Enable persistence**: For production, enable persistent volumes for model storage
4. **Use specific image tags**: Avoid `latest` tag in production
5. **Configure resource limits**: Prevent resource exhaustion
6. **Set up monitoring**: Use Prometheus/Grafana for observability
7. **Regular updates**: Keep dependencies and base images updated

## Next Steps

- [API Documentation](../README.md#api-endpoints)
- [Development Guide](../CONTRIBUTING.md)
- [Architecture Overview](../README.md#architecture)