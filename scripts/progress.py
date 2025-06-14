from tqdm import tqdm

def progress(desc, total, disable=False):
    return tqdm(total=total, desc=desc, disable=disable)