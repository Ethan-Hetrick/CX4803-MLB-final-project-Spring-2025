# We will train 5 models for the class project trained on the FCGR representations made from assemblies. We will test it on 3 tasks: Genus and species (Enterobacteriaecea dataset), and strain level (Salmonella dataset)

# 1. A classic image classifier: resnet50, resNext101, etc.
#     - Paper [here](https://ecoevorxiv.org/repository/view/6567/) describes methods
# 2. Unsupervised clustering approach: DeLUCS
#     - https://github.com/millanp95/DeLUCS
# 3. PanSpace FCGR architecture
#     - Publication: https://doi.org/10.1101/2025.03.19.644115
#     - GitHub: https://github.com/pg-space/panspace
# 4. Vision transformer (ViT)
#     - Paper [here](https://ecoevorxiv.org/repository/view/6567/) describes methods
# 5. Simple model: smashallow MLP, shallow 1D CNN, etc.
#     - Paper above also has examples of this

class ResNetClassifier(nn.Module):
    def __init__(self, etc):
        super(ResNetClassifier, self).__init__()
        
        # TODO: Implement initialization for ResNet50 and ResNeXt101
        
    def forward(self, x):
        # TODO: Implement feed forward
    
    return self.model(x)

class DeLUCS():
    pass
    
class panspace():
    pass

class ViTClassifier(nn.Module):
    pass
    
class ShallowMLPClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes):
        super(ShallowMLPClassifier, self).__init__()
        # TODO: Make layers
    
    def forward(self, x):
        # TODO: Forward function