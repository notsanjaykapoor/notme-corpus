import torch

def torch_device() -> str:
    """
    return supported pytorch device on this machine, should be one of 'cpu', 'mps', 'cuda'
    """
    if torch.cuda.is_available():
        return "cuda"

    if torch.backends.mps.is_available():
        return "mps"

    return "cpu"