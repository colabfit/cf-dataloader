# CF-DataLoader
A PyTorch-based DataLoader that streams data directly from the [ColabFit Exchange](colabfit.org).

## Installation
```
pip install git+https://github.com/colabfit/cf-dataloader.git
```

## Example
```python
from cf_dataloader import ColabFitStreamingDataset, ColabFitStreamingDataLoader
ds = ColabFitStreamingDataset(dataset_list=["DS_q4h7q8q0fnve_0"]) # DS ID obtained from online or CLI query
dl = ColabFitStreamingDataLoader(ds, graph_converter=None, batch_size=64, num_workers=8) 
```
