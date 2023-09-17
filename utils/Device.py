def detect_device() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except:
        try:
            import torch_directml
            return "dml"
        except:
            pass
    return "cpu"


def llm_device(device: str):
    if device == "cuda":
        import torch
        return torch.device("cuda")
    elif device == "mps":
        import torch
        return torch.device("mps")
    elif device == "dml":
        import torch_directml
        return torch_directml.device()
    elif device == "cpu":
        import torch
        return torch.device("cpu")
    else:
        raise ValueError(f"Unknown device {device}")