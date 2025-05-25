import torch
from torch import nn
import pandas as pd
import numpy as np

class Encoder(nn.Module):
    def __init__(self):
        super(Encoder, self).__init__()