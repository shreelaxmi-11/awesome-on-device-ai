# 🔨 Custom Adapter Builder

Pipeline to prepare data, run LoRA training, and export a reusable `.npz` adapter for any MLX-compatible model. See [lora_on_personal_data](../lora_on_personal_data/) for the full implementation.

## Quick Start

```bash
cd awesome-on-device-ai/finetuning/lora_on_personal_data
python train.py --prepare --input data.txt
python train.py --train
```

## Part of [Awesome On-Device AI](../../README.md)
