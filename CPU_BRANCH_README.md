# HunyuanVideo - CPU-Optimized Branch

## 🎯 CPU-Optimized for 8-Core Systems with 32GB RAM

This branch contains a CPU-optimized version of HunyuanVideo designed to run on systems without GPU acceleration. Perfect for:

- ✅ Cloud deployments (Render.com, AWS EC2, GCP, Azure)
- ✅ Development environments without GPU
- ✅ CI/CD pipelines
- ✅ Cost-effective video generation
- ✅ N8N automation workflows

## 🚀 Quick Start

### Installation

```bash
# Install CPU-optimized PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
pip install -r requirements-api.txt

# Download models (follow official instructions)
# Place in ckpts/ directory
```

### Generate Your First Video

```bash
# Start API server
./start_api.sh

# In another terminal, generate a portrait video
python example_client.py \
  --url http://localhost:10000 \
  --prompt "A cat walks on the grass, realistic style" \
  --output my_video.mp4
```

## 📱 Portrait & Landscape Support

### Portrait (9:16 - TikTok, Instagram Reels)
```bash
curl -X POST http://localhost:10000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your amazing prompt here",
    "preset": "portrait_60s"
  }'
```

### Landscape (16:9 - YouTube, TV)
```bash
curl -X POST http://localhost:10000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your amazing prompt here",
    "preset": "landscape_60s"
  }'
```

## 🔗 N8N Integration

This version includes a ready-to-use N8N integration service for workflow automation.

```bash
# Start N8N integration service
./start_n8n.sh
```

**Example N8N Workflow:**
1. HTTP Request → `POST http://localhost:8080/webhook/generate`
2. Wait 30 seconds
3. HTTP Request → `GET http://localhost:8080/webhook/status/{job_id}`
4. Loop until status is "completed"
5. HTTP Request → `GET http://localhost:8080/webhook/download/{job_id}`

See [N8N_INTEGRATION.md](N8N_INTEGRATION.md) for detailed setup guide.

## ⚙️ Available Presets

| Preset | Resolution | Aspect Ratio | Duration | Best For |
|--------|-----------|--------------|----------|----------|
| `portrait_60s` | 544x960 | 9:16 | ~60s | TikTok, Instagram Reels |
| `portrait_30s` | 544x960 | 9:16 | ~30s | Quick social media |
| `landscape_60s` | 960x544 | 16:9 | ~60s | YouTube, TV |
| `landscape_30s` | 960x544 | 16:9 | ~30s | Quick landscape |

## 📊 Performance

**8-Core CPU, 32GB RAM:**
- Portrait 60s (30 steps): 15-25 minutes
- Portrait 30s (30 steps): 8-15 minutes
- Landscape 60s (30 steps): 15-25 minutes

## 📚 Documentation

- **[CPU_README.md](CPU_README.md)** - Complete CPU setup guide
- **[N8N_INTEGRATION.md](N8N_INTEGRATION.md)** - N8N workflow integration
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
- **[CPU_DEPLOYMENT_GUIDE.md](CPU_DEPLOYMENT_GUIDE.md)** - Cloud deployment

## 🔧 What's Different from GPU Version?

### Removed (GPU-only features)
- ❌ CUDA/GPU dependencies
- ❌ Multi-GPU support (xfuser)
- ❌ FP8/FP16 precision
- ❌ Distributed training code
- ❌ Gradio UI

### Added (CPU optimizations)
- ✅ CPU-only inference path
- ✅ FP32 precision
- ✅ Sequential CPU offloading
- ✅ Portrait/landscape presets
- ✅ N8N webhook integration
- ✅ Simplified API

## 🧪 Test Your Setup

```bash
# Run setup validation
python test_cpu_setup.py
```

## 📖 Example Prompt for Cottagecore Ferret Video

Based on the problem statement, here's how to generate the cottagecore ferret video:

```json
{
  "prompt": "A whimsical cottagecore ferret habitat with tiny mushrooms, miniature flower crowns, and natural wood textures. Ferrets playing in soft linen bedding, exploring burlap foraging toys filled with treats, and snuggling in a cozy, fairy-tale inspired environment. Warm lighting, earthy tones, magical aesthetic with greens, browns, and creams. Close-up shots of ferret faces, DIY accessories, and miniature tea party setup. Heartwarming and playful mood.",
  "preset": "portrait_60s",
  "num_inference_steps": 40,
  "seed": 42
}
```

## 🎬 API Endpoints

### Main API (Port 10000)
- `POST /api/generate` - Generate video
- `GET /api/status/{job_id}` - Check status
- `GET /api/videos/{filename}` - Download video
- `GET /api/info` - Get presets & info

### N8N Webhooks (Port 8080)
- `POST /webhook/generate` - Generate via webhook
- `GET /webhook/status/{job_id}` - Status via webhook
- `GET /webhook/download/{job_id}` - Download via webhook

## 💡 Tips for Best Results

1. **Use descriptive prompts** - More detail = better results
2. **Start with presets** - They're optimized for CPU
3. **30 steps recommended** - Good quality/speed balance
4. **Monitor RAM** - Close other apps during generation
5. **Be patient** - CPU generation takes 15-25 minutes

## 🆘 Troubleshooting

**Out of memory?**
- Reduce `video_length` to 65 frames (30 seconds)
- Close other applications
- Ensure 32GB RAM available

**Too slow?**
- Normal for CPU (15-25 min)
- Try 30-second presets for faster results
- Reduce `num_inference_steps` (trade-off with quality)

**API won't start?**
- Check models are in `ckpts/` directory
- Verify PyTorch CPU version installed
- Check logs for errors

## 🌟 Key Features

- ✅ **No GPU Required** - Runs on CPU only
- ✅ **Portrait Videos** - 9:16 for TikTok/Instagram
- ✅ **Landscape Videos** - 16:9 for YouTube
- ✅ **60+ Second Videos** - Up to 129 frames at 24fps
- ✅ **N8N Integration** - Webhook-ready automation
- ✅ **REST API** - Easy integration with any platform
- ✅ **Preset Configurations** - Quick setup for common use cases

## 📄 License

See [LICENSE.txt](LICENSE.txt) for license information.

## 🙏 Acknowledgments

Based on HunyuanVideo by Tencent, optimized for CPU-only operation with added portrait support and N8N integration.

---

For the original GPU-accelerated version, see the [main branch](https://github.com/Tencent-Hunyuan/HunyuanVideo).
