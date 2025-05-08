from pathlib import Path

import numpy as np
import open_clip
import torch
from PIL import Image
from torch.nn.functional import normalize

from sqb.tools import extract_character, remove_empty_area

DEVICE: str = 'cuda' if torch.cuda.is_available() else 'cpu'
RECIPE: tuple[str, str] = ('ViT-L-14-quickgelu', 'dfn2b')

MODEL, _, PREPROCESS = open_clip.create_model_and_transforms(RECIPE[0], pretrained=RECIPE[1], device=DEVICE)
MODEL.eval()


def load_model(recipe: tuple[str, str] = ('ViT-L-14-quickgelu', 'dfn2b')):
    model, _, preprocess = open_clip.create_model_and_transforms(recipe[0], pretrained=recipe[1], device=DEVICE)
    model.eval()

    return model, preprocess


@torch.inference_mode()
def get_image_embedding(image: torch.Tesnor) -> torch.Tensor:
    image = PREPROCESS(image).unsqueeze(0).to(DEVICE)
    return normalize(MODEL.encode_image(image), p=2.0)


def get_query_embedding(query_image_path: Path | str) -> tuple[torch.Tensor, np.ndarray]:
    query_image = extract_character(query_image_path)
    query_image = remove_empty_area(query_image)
    query_image = Image.fromarray(query_image[..., ::-1])
    return get_image_embedding(query_image).reshape(1, -1), query_image


def get_document_embeddings(document_path: Path | str) -> torch.Tensor:
    document_images: list[Path] = sorted(Path(document_path).glob('*/*.png'))
    return torch.cat([get_image_embedding(Image.open(path)) for path in document_images], dim=0)


def get_similar_images(query_image_path: Path | str, documents_embeddings: torch.Tensor, top_k: int = 5) -> list[int]:
    query_embedding, _ = get_query_embedding(query_image_path)

    similarity = (100.0 * query_embedding @ documents_embeddings.T).softmax(dim=-1, dtype=torch.float32)

    _, indices = similarity[0].topk(top_k)

    return indices.cpu().numpy().tolist()
