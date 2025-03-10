''' Utilities to streamline the import of Caffenet in torch '''
import os
from os.path import join
import torch
import sys
sys.path.append("D:\Github\pytorch-caffe")
from caffenet import *  # Pytorch-caffe converter
import numpy as np
#%%
from sys import platform
if platform == "linux":  # CHPC cluster
    homedir = os.path.expanduser('~')
    netsdir = os.path.join(homedir, 'Generate_DB/nets')
else:
    if os.environ['COMPUTERNAME'] == 'DESKTOP-9DDE2RH':  # PonceLab-Desktop 3
        homedir = "D:/Generator_DB_Windows"
        netsdir = os.path.join(homedir, 'nets')
    elif os.environ['COMPUTERNAME'] == 'DESKTOP-MENSD6S':  # Home_WorkStation
        homedir = "D:/Monkey_Data/Generator_DB_Windows"
        netsdir = os.path.join(homedir, 'nets')
    else:
        homedir = os.path.expanduser('~')
        netsdir = os.path.join(homedir, 'Documents/nets')
#%% Prepare PyTorch version of the Caffe networks
def load_caffenet():
    netsdir = r"D:\Generator_DB_Windows\nets"
    protofile = join(netsdir, r"caffenet\caffenet.prototxt") # 'resnet50/deploy.prototxt'
    weightfile = join(netsdir, 'bvlc_reference_caffenet.caffemodel') # 'resnet50/resnet50.caffemodel'
    save_path = join(netsdir, r"caffenet\caffenet_state_dict.pt")
    net = CaffeNet(protofile)
    print(net)
    if os.path.exists(save_path):
        net.load_state_dict(torch.load(save_path))
    else:
        net.load_weights(weightfile)
        torch.save(net.state_dict(), save_path)
    net.eval()
    net.verbose = False
    net.requires_grad_(requires_grad=False)
    for param in net.parameters():
        param.requires_grad = False
    return net

def load_generator():
    netsdir = r"D:/Generator_DB_Windows/nets"
    save_path = os.path.join(netsdir, r"upconv/fc6/generator_state_dict.pt")
    protofile = os.path.join(netsdir, r"upconv/fc6/generator.prototxt")  # 'resnet50/deploy.prototxt'
    weightfile = os.path.join(netsdir, r'upconv/fc6/generator.caffemodel')  # 'resnet50/resnet50.caffemodel'
    Generator = CaffeNet(protofile)
    print(Generator)
    if os.path.exists(save_path):
        Generator.load_state_dict(torch.load(save_path))
    else:
        Generator.load_weights(weightfile)
        Generator.save(Generator.state_dict(), save_path)
    Generator.eval()
    Generator.verbose = False
    Generator.requires_grad_(requires_grad=False)
    for param in Generator.parameters():
        param.requires_grad = False
    return Generator

#%%
BGR_mean = torch.tensor([104.0, 117.0, 123.0])
BGR_mean = torch.reshape(BGR_mean, (1, 3, 1, 1))
#%%
def visualize(G, code):
    """Do the De-caffe transform (Validated)
    works for a single code """
    code = code.reshape(-1, 4096).astype(np.float32)
    blobs = G(torch.from_numpy(code))
    out_img = blobs['deconv0']  # get raw output image from GAN
    clamp_out_img = torch.clamp(out_img + BGR_mean, 0, 255)
    vis_img = clamp_out_img[:, [2, 1, 0], :, :].permute([2, 3, 1, 0]).squeeze() / 255
    return vis_img

def preprocess(img):
    return img
# import net_utils
# detfmr = net_utils.get_detransformer(net_utils.load('generator'))
# tfmr = net_utils.get_transformer(net_utils.load('caffe-net'))

