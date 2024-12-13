from torch.utils.data import Dataset, DataLoader
from ase import Atoms
from functools import partial
import torch
import tqdm
import os
import sys
import time
import json
import numpy as np
import requests

# TODO: Need to specify training labels and sampling rate using WeightedRandomSampler
class ColabFitStreamingDataset(Dataset):
    '''
    Streaming Dataset which grabs data from ColabFit when used with the accompanying collate function and DataLoader.

    dataset_list is a list of ColabFit dataset IDs. These can be found online at colabfit.org or found via the CF-CLI tool.
    '''
    def __init__(self, database="ndb.colabfit-prod.prod", dataset_list=None, list_in_memory=True):
        self.dataset_list = sorted(dataset_list)
        if list_in_memory:
            self.po_list = self.get_po_list(dataset_list)
        else: # TODO: Write to file
            raise Exception("Only list_in_memory=True is currently supported")

    def get_po_list(self, datasets):
        query = {'datasets': datasets}
        results = requests.post('https://cf.hsrn.nyu.edu/po',json=query)
        pylist = results.json()
        return pylist

    def __len__(self):
        return len(self.po_list)


    def __getitem__(self,idx):
        return self.po_list[idx]






def ColabFitCollate(po_list, dataset_list, graph_converter=None):
    '''
    Collate function to be used in conjunction with the ColabFitStreamingDataset and ColabFitStreamingDataLoader
    '''
    query = {'po_list': po_list}
    results = requests.post('https://cf.hsrn.nyu.edu/dataloader',json=query)
    pylist = results.json() 
    atoms_list = []
    for l in pylist:
        l['forces'] = json.loads(l['forces'])
        l['stress'] = json.loads(l['stress'])
        l['atomic_numbers'] = json.loads(l['atomic_numbers'])
        l['cell'] = json.loads(l['cell'])
        l['positions'] = json.loads(l['positions_00'])
        l['dataset_idx'] = dataset_list.index(l['dataset_id'])
        #convert to atoms
        atoms = Atoms(numbers=l['atomic_numbers'],positions=l['positions'],cell=l['cell'],pbc=l['pbc'])
        atoms.info['dataset_idx']=l['dataset_idx']
        atoms.info['po_id']=l['po_id']
        atoms.info['co_id']=l['co_id']
        atoms.info['energy']=l['energy']
        atoms.info['stress']=l['stress']
        atoms.arrays['forces']=np.array(l['forces'])
        if graph_converter:
            atoms_list.append(graph_converter.convert(atoms))
        else:
            atoms_list.append(atoms)

    return atoms_list

class ColabFitStreamingDataLoader(DataLoader):       

    def __init__(self, ds=None, graph_converter=None, **kwargs):
        super().__init__(ds,**kwargs)
        self.collate_fn = partial(ColabFitCollate,dataset_list=self.dataset.dataset_list,graph_converter=graph_converter)

if __name__ == "__main__":

    ds = ColabFitStreamingDataset(dataset_list=["DS_q4h7q8q0fnve_0"])
    print (len(ds.po_list))
    #dl = ColabFitStreamingDataLoader(ds,batch_size=64,num_workers=16,graph_converter=ToGraphs(r_energy=True,r_forces=True))
    dl = ColabFitStreamingDataLoader(ds,batch_size=64,num_workers=2)
    s = time.time()
    t = []
    for i in tqdm.tqdm(dl):
        t.append(time.time()-s)
        s = time.time()
    print (np.mean(t))
