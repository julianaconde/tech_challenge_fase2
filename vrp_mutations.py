from __future__ import annotations

import random
from typing import List, TypeVar

T = TypeVar("T")


def swap_mutation(seq: List[T]) -> List[T]:
    if len(seq) < 2:
        return seq
    a, b = random.sample(range(len(seq)), 2)
    seq[a], seq[b] = seq[b], seq[a]
    return seq


def relocate_mutation(seq: List[T]) -> List[T]:
    if len(seq) < 2:
        return seq
    i = random.randrange(len(seq))
    elem = seq.pop(i)
    j = random.randrange(len(seq) + 1)
    seq.insert(j, elem)
    return seq


def two_opt_mutation(seq: List[T]) -> List[T]:
    if len(seq) < 4:
        return seq
    i = random.randrange(len(seq) - 1)
    j = random.randrange(i + 1, len(seq))
    seq[i:j] = reversed(seq[i:j])
    return seq


def mutate_vrp(seq: List[T], mutation_probability: float) -> List[T]:
    if random.random() >= mutation_probability:
        return seq
    op = random.choice([swap_mutation, relocate_mutation, two_opt_mutation])
    return op(seq)
