# Deployment Checklist for Render.com

Use this checklist to ensure a smooth deployment of HunyuanVideo on Render.com.

## Pre-Deployment Checklist

### 1. Account and Access
- [ ] Render.com account created
- [ ] GPU access enabled on Render.com account
- [ ] GitHub account connected to Render.com
- [ ] Repository forked or accessible

### 2. Model Preparation
- [ ] Hugging Face account created (for model download)
- [ ] Model checkpoints downloaded (40GB+)
  - Use: `huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts`
- [ ] Model storage plan determined:
  - [ ] Option A: Upload to cloud storage (S3, GCS, etc.)
  - [ ] Option B: Download via SSH after deployment
  - [ ] Option C: Download during startup (not recommended)

### 3. Cost Understanding
- [ ] Reviewed Render.com GPU pricing
- [ ] Understood monthly cost (~$1,000-$2,000 for 24/7)
- [ ] Budget approved for GPU instances
- [ ] Persistent disk cost considered (~$25/month for 100GB)

### 4. Repository Setup
- [ ] All deployment files present in repository:
  - [ ] `render.yaml`
  - [ ] `Dockerfile`
  - [ ] `docker-compose.yml`
  - [ ] `start.sh`
  - [ ] `healthcheck.py`
  - [ ] `.env.example`
  - [ ] `DEPLOYMENT.md`
  - [ ] `QUICKSTART.md`
  - [ ] Updated `.gitignore`
  - [ ] Updated `README.md`

## Deployment Checklist

### Option A: Blueprint Deployment (Recommended)

- [ ] Repository pushed to GitHub
- [ ] Logged into Render.com Dashboard
- [ ] Clicked "New +" → "Blueprint"
- [ ] Connected GitHub repository
- [ ] Render detected `render.yaml` file
- [ ] Reviewed configuration:
  - [ ] Service name: `hunyuan-video`
  - [ ] Environment: Docker
  - [ ] GPU instance selected (minimum 60GB VRAM)
  - [ ] Persistent disk configured (100GB)
- [ ] Environment variables verified:
  - [ ] `SERVER_NAME=0.0.0.0`
  - [ ] `SERVER_PORT=10000`
  - [ ] `MODEL_BASE=/opt/render/project/src/ckpts`
  - [ ] `SAVE_PATH=/opt/render/project/src/results`
  - [ ] `GRADIO_ANALYTICS_ENABLED=False`
- [ ] Clicked "Apply" to start deployment
- [ ] Deployment started (monitor logs)

### Option B: Manual Deployment

- [ ] Logged into Render.com Dashboard
- [ ] Clicked "New +" → "Web Service"
- [ ] Connected GitHub repository
- [ ] Configured service:
  - [ ] Name: `hunyuan-video`
  - [ ] Environment: Docker
  - [ ] Region: Selected (GPU available)
  - [ ] Branch: `main` or deployment branch
  - [ ] Dockerfile path: `./Dockerfile`
- [ ] Selected instance type:
  - [ ] GPU instance with 60GB+ VRAM
- [ ] Added environment variables (see above)
- [ ] Added persistent disk:
  - [ ] Name: `model-storage`
  - [ ] Mount path: `/opt/render/project/src/ckpts`
  - [ ] Size: 100GB
- [ ] Clicked "Create Web Service"
- [ ] Deployment started (monitor logs)

## Post-Deployment Checklist

### 1. Verify Deployment
- [ ] Build completed successfully (check logs)
- [ ] Service is "Live" in dashboard
- [ ] No errors in application logs
- [ ] Service URL is accessible

### 2. Upload Models
Choose one method:

#### Method A: SSH Upload (Recommended)
- [ ] Enabled SSH in Render dashboard
- [ ] Connected via SSH: `render ssh hunyuan-video`
- [ ] Navigated to ckpts: `cd /opt/render/project/src/ckpts`
- [ ] Installed HF CLI: `pip install huggingface-hub`
- [ ] Downloaded models: `huggingface-cli download tencent/HunyuanVideo --local-dir .`
- [ ] Verified model structure exists
- [ ] Restarted service in Render dashboard

#### Method B: Cloud Storage
- [ ] Models uploaded to S3/GCS
- [ ] Download script added to `start.sh`
- [ ] Service redeployed
- [ ] Models downloaded to persistent disk
- [ ] Verified model files exist

### 3. Test Application
- [ ] Accessed service URL
- [ ] Gradio interface loaded
- [ ] Entered test prompt: "A cat walks on the grass, realistic style."
- [ ] Selected resolution: `1280x720`
- [ ] Set video length: `129 frames (5s)`
- [ ] Set inference steps: `50`
- [ ] Clicked "Generate"
- [ ] Video generation started (check logs)
- [ ] Video generated successfully (5-10 minutes)
- [ ] Video downloaded and plays correctly

### 4. API Test
- [ ] Installed gradio_client: `pip install gradio_client`
- [ ] Tested API with Python script
- [ ] Received video response
- [ ] Verified video quality

### 5. Monitoring Setup
- [ ] Set up alerts in Render dashboard
- [ ] Configured health check monitoring
- [ ] Set up cost alerts/budgets
- [ ] Documented service URL and credentials

## Configuration Verification

### Environment Variables
```bash
# Verify these are set correctly:
SERVER_NAME=0.0.0.0
SERVER_PORT=10000
MODEL_BASE=/opt/render/project/src/ckpts
SAVE_PATH=/opt/render/project/src/results
GRADIO_ANALYTICS_ENABLED=False
PYTHONUNBUFFERED=1
```

### Model Directory Structure
```
/opt/render/project/src/ckpts/
└── hunyuan-video-t2v-720p/
    ├── transformers/
    │   └── mp_rank_00_model_states.pt
    ├── vae/
    └── text_encoder/
```

### Persistent Disk
- [ ] Mounted at: `/opt/render/project/src/ckpts`
- [ ] Size: 100GB minimum
- [ ] Models stored and accessible

## Optimization Checklist

### Performance
- [ ] Considered FP8 weights (saves ~10GB memory)
- [ ] Reviewed inference step count (lower = faster)
- [ ] Set default resolution appropriately
- [ ] Enabled CPU offload (already in config)

### Cost Optimization
- [ ] Set up auto-scaling if available
- [ ] Configured sleep/suspend during low usage
- [ ] Implemented rate limiting
- [ ] Set up usage monitoring

### Security
- [ ] Considered authentication (if needed)
- [ ] Set up HTTPS (provided by Render)
- [ ] Reviewed API access controls
- [ ] Configured CORS if needed

## Troubleshooting Checklist

If deployment fails, check:

### Build Issues
- [ ] Docker build logs reviewed
- [ ] Base image is accessible
- [ ] All dependencies install correctly
- [ ] Flash-attention build (optional, can fail)

### Runtime Issues
- [ ] Service logs reviewed
- [ ] GPU is available and detected
- [ ] Models are in correct location
- [ ] Environment variables set correctly
- [ ] Persistent disk mounted properly

### Generation Issues
- [ ] GPU memory sufficient (60GB+)
- [ ] CPU offload enabled
- [ ] Inference steps reasonable (30-50)
- [ ] Resolution appropriate for GPU

### Performance Issues
- [ ] GPU utilization checked
- [ ] Memory usage monitored
- [ ] Network bandwidth adequate
- [ ] Disk I/O not bottleneck

## Maintenance Checklist

### Weekly
- [ ] Review usage logs
- [ ] Check costs vs budget
- [ ] Monitor GPU utilization
- [ ] Review generated videos quality

### Monthly
- [ ] Review and optimize costs
- [ ] Update dependencies if needed
- [ ] Check for model updates
- [ ] Backup persistent disk (if needed)

### As Needed
- [ ] Scale instance size if needed
- [ ] Update configuration
- [ ] Apply security patches
- [ ] Optimize performance

## Documentation Reference

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Summary**: See [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
- **Original Docs**: [HunyuanVideo GitHub](https://github.com/Tencent-Hunyuan/HunyuanVideo)

## Support Resources

- **Render Docs**: https://render.com/docs
- **Render Support**: support@render.com
- **GitHub Issues**: https://github.com/Devilhere444/HunyuanVideo/issues (this fork)
- **Original Repository**: https://github.com/Tencent-Hunyuan/HunyuanVideo
- **HunyuanVideo Docs**: https://github.com/Tencent-Hunyuan/HunyuanVideo

## Success Criteria

Your deployment is successful when:
- ✅ Service is "Live" in Render dashboard
- ✅ URL is accessible and shows Gradio interface
- ✅ Models are loaded and accessible
- ✅ Test video generates successfully
- ✅ Video quality is acceptable
- ✅ Generation time is reasonable (5-15 min)
- ✅ No errors in logs
- ✅ Costs are within budget

## Notes

- First deployment may take 30-60 minutes (Docker build + setup)
- Model download can take 1-3 hours depending on method
- First video generation may be slower (model loading)
- Expect 5-15 minutes per video generation
- Monitor costs closely in first week

---

**Last Updated**: 2024
**Repository**: Devilhere444/HunyuanVideo
**Deployment Target**: Render.com
