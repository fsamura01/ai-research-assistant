import torch_directml
import torch

def test_directml():
    print("--- 🩺 AMD GPU Diagnostic ---")
    try:
        device = torch_directml.device()
        device_count = torch_directml.device_count()
        device_names = torch_directml.list_devices()
        
        print(f"✅ DirectML detected!")
        print(f"📍 Device Count: {device_count}")
        print(f"🖥️  GPU Name: {device_names[0] if device_names else 'Unknown'}")
        
        # Simple tensor test
        t1 = torch.tensor([1.0, 2.0, 3.0]).to(device)
        t2 = torch.tensor([4.0, 5.0, 6.0]).to(device)
        t3 = t1 + t2
        
        print(f"🧪 Tensor Addition Test: {t3.cpu().numpy()} (on {device})")
        print("🚀 Status: READY FOR ACCELERATION")
        
    except Exception as e:
        print(f"❌ Diagnostic Failed: {e}")

if __name__ == "__main__":
    test_directml()
