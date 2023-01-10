import torch
from torch import Tensor

def iou_coeff(input: Tensor, target: Tensor, reduce_batch_first: bool = False):
    # Average of iou coefficient for all batches, or for a single mask
    assert input.size() == target.size()
    assert input.dim() == 3 or not reduce_batch_first

    sum_dim = (-1, -2) if input.dim() == 2 or not reduce_batch_first else (-1, -2, -3)

    inter =  (input * target).sum(dim=sum_dim)

    sets_sum = input.sum(dim=sum_dim) + target.sum(dim=sum_dim)
    sets_sum = torch.where(sets_sum == 0, inter, sets_sum)

    union = sets_sum - inter

    iou = inter / union
    return iou.mean()

def multiclass_iou_coeff(input: Tensor, target: Tensor, reduce_batch_first: bool = False, epsilon: float = 1e-6):
    # Average of iou coefficient for all classes
    return iou_coeff(input.flatten(0, 1), target.flatten(0, 1), reduce_batch_first)

def iou_loss(input: Tensor, target: Tensor, multiclass: bool = False):
    fn = multiclass_iou_coeff if multiclass else iou_coeff
    return 1 - fn(input, target, reduce_batch_first=True)