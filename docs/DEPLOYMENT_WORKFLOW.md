# Deployment Workflow Guide

This guide explains when and how to use each deployment method.

## Deployment Methods Overview

### 1. PR Comment Deployment (Testing)
**When to use**: Before merging to main, to test your changes
**Trigger**: Comment on an open PR
**Purpose**: Test your PR changes in a live environment

### 2. Main Branch Deployment (Production)
**When to use**: After merging to main
**Trigger**: Automatic on merge to main
**Purpose**: Deploy to production AKS

## Detailed Workflows

### Testing Changes with PR Comments

This is the **recommended workflow** for testing changes before merging:

```
1. Create a feature branch
   git checkout -b feature/my-changes

2. Make your changes and commit
   git add .
   git commit -m "Add new feature"

3. Push to GitHub
   git push origin feature/my-changes

4. Create a Pull Request
   - Go to GitHub
   - Click "New Pull Request"
   - Select your branch
   - Create the PR

5. Wait for tests to pass (optional but recommended)
   - Check the "Checks" tab on your PR
   - Ensure build-and-test passes

6. Add a deployment comment to test your changes
   - Go to the PR conversation tab
   - Add a new comment with ONLY:
     /deploy aks
   OR
     /deploy openshift

7. Watch the deployment
   - Go to Actions tab
   - See the workflow run
   - Wait for success comment on PR

8. Test your deployed changes
   - Use the URL from the PR comment
   - Verify your changes work

9. If everything works, merge the PR
   - Click "Merge pull request"
   - This triggers automatic deployment to production AKS
```

### Production Deployment (Main Branch)

This happens **automatically** when you merge to main:

```
1. Merge PR to main
   - Click "Merge pull request" on GitHub
   OR
   - git checkout main
   - git merge feature/my-changes
   - git push origin main

2. Automatic deployment starts
   - Workflow: deploy-aks job runs
   - Deploys to production AKS cluster
   - Uses image tag from charts/values.yaml

3. Verify deployment
   - Check Actions tab for status
   - Verify pods are running in AKS
```

## Comment Deployment Examples

### Example 1: Testing on AKS

```markdown
**Scenario**: You added a new API endpoint and want to test it before merging

1. Create PR with your changes
2. Comment on the PR:
   /deploy aks
3. Wait for deployment (2-5 minutes)
4. You'll get a comment like:
   ✅ Successfully deployed to AKS!
   **Namespace:** ai-monitoring
   **Image Tag:** abc123def
5. Test your endpoint:
   kubectl port-forward -n ai-monitoring svc/ml-service 8000:8000
   curl http://localhost:8000/api/v1/your-new-endpoint
6. If it works, merge the PR
```

### Example 2: Testing on OpenShift

```markdown
**Scenario**: You need to test OpenShift-specific configurations

1. Create PR with your changes
2. Comment on the PR:
   /deploy openshift
3. Wait for deployment (2-5 minutes)
4. You'll get a comment like:
   ✅ Successfully deployed to OpenShift!
   **Route URL:** https://ml-service-ai-monitoring.apps.cluster.example.com
   **Namespace:** ai-monitoring
   **Image Tag:** abc123def
5. Test via the Route URL:
   curl https://ml-service-ai-monitoring.apps.cluster.example.com/api/v1/health
6. If it works, merge the PR
```

## Common Scenarios

### Scenario 1: "I want to test my changes before merging"
✅ Use PR comment deployment
- Create PR
- Comment `/deploy aks` or `/deploy openshift`
- Test the deployment
- Merge when satisfied

### Scenario 2: "I merged to main and it's deploying automatically"
✅ This is correct behavior
- Main branch always deploys to production AKS
- No comment needed
- This is the production deployment

### Scenario 3: "I want to deploy to OpenShift production"
❌ Not currently supported automatically
✅ Options:
1. Use PR comment `/deploy openshift` to test
2. Manually deploy to OpenShift production:
   ```bash
   oc login --token=<token> --server=<server>
   helm upgrade --install ml-service ./charts \
     -f charts/values.yaml \
     -f charts/values-openshift.yaml \
     --set image.tag=<version>
   ```

### Scenario 4: "My comment deployment isn't working"
Check these:
1. ✅ Is the PR still open? (Not merged or closed)
2. ✅ Do you have write access to the repo?
3. ✅ Is the comment exactly `/deploy aks` or `/deploy openshift`?
4. ✅ Are the required secrets configured?
5. ✅ Check the Actions tab for error messages

## Troubleshooting

### Comment Not Triggering Workflow

**Problem**: You commented `/deploy aks` but nothing happened

**Solutions**:
1. Check if PR is open (not merged/closed)
2. Verify comment format is exact:
   - ✅ `/deploy aks`
   - ✅ `/deploy openshift`
   - ❌ `/deploy aks please`
   - ❌ `Can you /deploy aks`
3. Check you have write access:
   - Go to repo Settings → Collaborators
   - Verify you're listed with write/admin access
4. Check Actions tab for workflow runs
5. Look for error messages in workflow logs

### Deployment Failed

**Problem**: Workflow ran but deployment failed

**Solutions**:
1. Check the workflow logs in Actions tab
2. Common issues:
   - Missing secrets (AZURE_CREDENTIALS, OPENSHIFT_TOKEN, etc.)
   - Cluster authentication failed
   - Image pull errors
   - Resource quota exceeded
3. Check the failure comment on your PR for details
4. Click the workflow run link in the comment

### Multiple Deployments

**Problem**: I commented multiple times and now there are multiple deployments

**Solution**:
- Each comment triggers a new deployment
- The latest deployment will replace the previous one
- Wait for the current deployment to finish before commenting again

## Best Practices

1. **Test Before Merging**
   - Always use PR comment deployment to test changes
   - Don't merge until you've verified the deployment works

2. **One Comment at a Time**
   - Wait for deployment to complete before commenting again
   - Check Actions tab for status

3. **Use Correct Format**
   - Comment must be exactly `/deploy aks` or `/deploy openshift`
   - No extra text on the same line

4. **Check Secrets**
   - Ensure all required secrets are configured
   - Test with a simple PR first

5. **Monitor Deployments**
   - Watch the Actions tab
   - Read the feedback comments on your PR
   - Check pod logs if something fails

## Quick Reference

| Action | When | How | Result |
|--------|------|-----|--------|
| Test on AKS | Before merge | Comment `/deploy aks` on PR | Deploys PR code to AKS |
| Test on OpenShift | Before merge | Comment `/deploy openshift` on PR | Deploys PR code to OpenShift |
| Deploy to Production | After merge | Merge PR to main | Auto-deploys to production AKS |
| Manual OpenShift | Anytime | Use `oc` and `helm` commands | Manual deployment |

## Need Help?

1. Check workflow logs in Actions tab
2. Read error messages in PR comments
3. Review this guide
4. Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed setup
5. Verify secrets are configured correctly