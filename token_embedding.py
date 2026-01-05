import os
import torch
from torch import nn
import torch

class TokenEmbedding:
    """Token Embedding."""
    def __init__(self, embedding_name):
        self.idx_to_token, self.idx_to_vec = self._load_embedding(
            embedding_name)
        self.unknown_idx = 0
        self.token_to_idx = {token: idx for idx, token in
                             enumerate(self.idx_to_token)}

    def _load_embedding(self, embedding_name):
        idx_to_token, idx_to_vec = ['<unk>'], []
        data_dir = embedding_name

        with open(os.path.join(data_dir, 'vec.txt'), 'r') as f:
            for line in f:
                elems = line.rstrip().split(' ')
                token, elems = elems[0], [float(elem) for elem in elems[1:]]
                if len(elems) > 1:
                    idx_to_token.append(token)
                    idx_to_vec.append(elems)
        idx_to_vec = [[0] * len(idx_to_vec[0])] + idx_to_vec
        return idx_to_token, torch.tensor(idx_to_vec)

    def get_closest_token(self, x: torch.Tensor, exclude: list[str]=[]) -> str:
        topk, cos = knn(self.idx_to_vec, x, len(exclude) + 1)
        for i in range(len(exclude) + 1):
            if self.idx_to_token[int(topk[i])] not in exclude:
                break

        return self.idx_to_token[int(topk[i])]

    def __getitem__(self, tokens):
        indices = [self.token_to_idx.get(token, self.unknown_idx)
                   for token in tokens]
        vecs = self.idx_to_vec[torch.tensor(indices)]
        return vecs

    def __len__(self):
        return len(self.idx_to_token)

def knn(W, x, k):
    # Add 1e-9 for numerical stability
    cos = torch.mv(W, x.reshape(-1,)) / (
        torch.sqrt(torch.sum(W * W, axis=1) + 1e-9) *
        torch.sqrt((x * x).sum()))
    _, topk = torch.topk(cos, k=k)
    return topk, [cos[int(i)] for i in topk]


def get_analogy(token_a, token_b, token_c, embed):
    vecs = embed[[token_a, token_b, token_c]]
    x = vecs[1] - vecs[0] + vecs[2]

    topk, cos = knn(embed.idx_to_vec, x, 10)
    for i in range(10):
        if embed.idx_to_token[int(topk[i])] not in [token_a, token_b, token_c]:
            break

    return embed.idx_to_token[int(topk[i])]

def get_similar_tokens(query_token, k, embed):
    topk, cos = knn(embed.idx_to_vec, embed[[query_token]], k + 1)
    for i, c in zip(topk[1:], cos[1:]):
        print(f'cosine sim={float(c):.3f}: {embed.idx_to_token[int(i)]}')



if __name__ == "__main__":
    glove_6b50d = TokenEmbedding('glove.2024.wikigiga.50d')

    print("Vocab size: " + str(len(glove_6b50d)))

    print(glove_6b50d.token_to_idx['beautiful'], glove_6b50d.idx_to_token[3516])


    get_similar_tokens("man", 20, glove_6b50d)
    print(get_analogy("hungry", "thirsty", "food", glove_6b50d))

    import code
    vars = globals().copy()
    vars.update(locals())
    code.interact(local=vars)