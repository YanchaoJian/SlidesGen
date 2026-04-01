import torch

# 检查 CUDA 是否可用
print("CUDA 是否可用:", torch.cuda.is_available())
print("PyTorch 版本:", torch.__version__)

if torch.cuda.is_available():
    print("GPU 数量:", torch.cuda.device_count())
    print("当前 GPU:", torch.cuda.get_device_name(0))
    print("CUDA 版本:", torch.version.cuda)
    
    # 简单的 GPU 张量运算测试
    x = torch.rand(3, 3).cuda()
    y = torch.rand(3, 3).cuda()
    z = x @ y
    print("\nGPU 矩阵乘法结果:\n", z)
else:
    print("未检测到 GPU，使用 CPU 运行")