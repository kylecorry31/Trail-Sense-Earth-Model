from tqdm import tqdm

def progress(desc, total):
    return tqdm(total=total, desc=desc)