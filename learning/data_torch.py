import time
import classes.torch_extractor as torch_extractor
import json 
import sys 

"""
    the script master/prepare_training.py extracts data for training
    and store them into a csv file.
    This script creates for every sample two .pt files:
    One for the features and one for the labels and store them
    respectively in "./learning/data/samples/" and "./learning/data/labels/"
"""
# python learning/data_torch.py parameters/data.json parameters/torch_extractors.json parameters/prepare_training.json
def main():
    args = sys.argv

    s = time.time()
    # extractor = torch_extractor.TorchExtractor(args[1],args[2],args[3])
    extractor = torch_extractor.TorchExtractor(args[1],args[2])

    # extractor = torch_extractor.TorchExtractor("parameters/data.json","parameters/torch_extractors.json")

    extractor.extract_tensors_sophie()
    print(time.time()-s)
       
   

if __name__ == "__main__":
    main()




