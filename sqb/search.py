from pathlib import Path

import clip
import cv2
import torch
from PIL import Image
from torch.nn.functional import normalize

from sqb.tools import extract_character, remove_empty_area

DEVICE: str = 'cuda' if torch.cuda.is_available() else 'cpu'
BACKBONE: str = 'ViT-L/14'
MODEL, PREPROCESS = clip.load(BACKBONE, device='cuda' if torch.cuda.is_available() else 'cpu')


def load_model(backbone: str = 'ViT-L/14'):
    return clip.load(backbone, device=DEVICE)


@torch.inference_mode()
def get_image_embedding(image_path: Path | str) -> torch.Tensor:
    image = PREPROCESS(Image.open(image_path)).unsqueeze(0).to(DEVICE)
    return normalize(MODEL.encode_image(image), p=2.0)


def get_query_embedding(query_image_path: Path | str) -> torch.Tensor:
    query_image = remove_empty_area(extract_character(query_image_path))
    cv2.imwrite('query.png', query_image)

    return get_image_embedding('query.png').reshape(1, -1)


def get_document_embeddings(document_path: Path | str) -> torch.Tensor:
    document_images: list[Path] = sorted(Path(document_path).glob('*/*.png'))
    return torch.cat([get_image_embedding(path) for path in document_images], dim=0)


def get_similar_images(query_image_path: Path | str, documents_embeddings: torch.Tensor, top_k: int = 5) -> list[int]:
    query_embedding = get_query_embedding(query_image_path)

    similarity = (100.0 * query_embedding @ documents_embeddings.T).softmax(dim=-1, dtype=torch.float32)

    _, indices = similarity[0].topk(top_k)

    return indices.cpu().numpy().tolist()
