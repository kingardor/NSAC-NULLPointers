from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .sample.ctdet import CTDetDataset

from .dataset.objdet import OBJdet


dataset_factory = {
    'objdet': OBJdet,
}

_sample_factory = {
    'objdet': CTDetDataset,
}


def get_dataset(dataset, task):
    class Dataset(dataset_factory[dataset], _sample_factory[task]):
        pass
    return Dataset
