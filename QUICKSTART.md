# Quick Start - Render.com Deployment

## Prerequisites Checklist

- [ ] Render.com account with GPU access
- [ ] GitHub account
- [ ] Repository forked/cloned
- [ ] Model checkpoints ready (40GB+)

## 5-Minute Deployment Guide

### Step 1: Prepare Models (Do this first!)

Download model checkpoints locally:
```bash
pip install huggingface-hub
huggingface-cli download tencent/HunyuanVideo --local-dir ./ckpts
```

**Note**: Models are ~40GB+. This will take time.

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add Render.com deployment config"
git push origin main
```

### Step 3: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml`
5. Click **"Apply"**

### Step 4: Upload Models

After deployment:

**Option A**: Via SSH (Recommended)
1. Enable SSH in Render dashboard
2. SSH into instance:
   ```bash
   render ssh <your-service-name>
   ```
3. Download models:
   ```bash
   cd /opt/render/project/src/ckpts
   pip install huggingface-hub
   huggingface-cli download tencent/HunyuanVideo --local-dir .
   ```

**Option B**: Use cloud storage
1. Upload models to S3/GCS
2. Add download script to `start.sh`

### Step 5: Access Your App

Your app will be available at:
```
https://your-service-name.onrender.com
```

## Test Locally First (Optional)

### Using Docker Compose

```bash
# 1. Build and start
docker-compose up --build

# 2. Access at http://localhost:8081
```

### Using Python Directly

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run server
python gradio_server.py --flow-reverse --use-cpu-offload

# 3. Access at http://localhost:8081
```

## Input Format

### Via Web Interface

1. Open the URL in your browser
2. Enter prompt: `"A cat walks on the grass, realistic style."`
3. Select resolution (e.g., `1280x720`)
4. Choose video length: `5s (129f)`
5. Set inference steps: `50`
6. Click **"Generate"**
7. Wait 5-10 minutes for generation
8. Download the generated video

### Via API

```python
from gradio_client import Client

client = Client("https://your-service-name.onrender.com")

result = client.predict(
    prompt="A cat walks on the grass, realistic style.",
    resolution="1280x720",
    video_length=129,
    seed=-1,
    num_inference_steps=50,
    guidance_scale=1.0,
    flow_shift=7.0,
    embedded_guidance_scale=6.0,
    api_name="/predict"
)

print(f"Generated video: {result}")
```

### Example Prompts

```
"A cat walks on the grass, realistic style."
"A person walking in the rain with an umbrella, cinematic lighting."
"Ocean waves crashing on a beach at sunset, drone view."
"A bustling city street at night with neon lights."
"Cherry blossoms falling in slow motion, spring season."
```

## Troubleshooting

### Service won't start?
- Check logs in Render dashboard
- Verify GPU instance is selected
- Ensure persistent disk is mounted

### Out of memory?
- Use smaller resolution (544x960)
- Enable CPU offload (already in config)
- Reduce inference steps to 30-40

### Models not found?
- Check `MODEL_BASE` environment variable
- Verify models are in `/opt/render/project/src/ckpts`
- Check persistent disk is mounted

### Generation too slow?
- Lower resolution
- Reduce inference steps
- Use FP8 weights (if available)

## Important Notes

⚠️ **GPU Required**: This application requires a GPU with 45-60GB VRAM

⚠️ **Cost Warning**: GPU instances are expensive (~$1000+/month for 24/7)

⚠️ **Generation Time**: Each video takes 5-15 minutes to generate

⚠️ **Model Size**: Checkpoints are ~40GB+ (requires persistent storage)

## Next Steps

- Read full [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- Configure auto-scaling to reduce costs
- Set up monitoring and alerts
- Implement rate limiting
- Add authentication if needed

## Support

- GitHub Issues: [Report issues](https://github.com/Devilhere444/HunyuanVideo/issues)
- Original Repo: [HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo)
- Render Docs: [render.com/docs](https://render.com/docs)
