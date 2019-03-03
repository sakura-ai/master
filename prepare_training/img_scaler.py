import skimage
import json
import helpers
import sys

class ImgScaler():
    def __init__(self,data,target_size):
        data = json.load(open(data))
        self.target_size = target_size
        self.original_image = data["original_images"] + "{}.jpg"
        self.destination_image = data["prepared_images"] + "{}.jpg"

    def scale(self,scene):
        
        img = skimage.io.imread(self.original_image.format(scene))
        biggest_dim = max(img.shape[0],img.shape[1])
        ratio = self.target_size/float(biggest_dim)
        img = skimage.transform.rescale(img,ratio,anti_aliasing= True,mode='constant',multichannel=True)
        
        img = self.__pad(img)
        helpers.remove_file(self.destination_image.format(scene))
        skimage.io.imsave(self.destination_image.format(scene),img)
        
  
            

    def __pad(self,img):
        pad0 = self.__get_padding(img.shape[0])
        pad1 = self.__get_padding(img.shape[1])
        pad2 = (0,0)
        paddings = [pad0,pad1,pad2]


        img = skimage.util.pad(img,paddings,'constant', constant_values=(0,0))
        return img

    def __get_padding(self,dim):
        dim = self.target_size - dim
        padding = [0,0]
        if dim != 0:
            padding[0] = int(dim/2)
            padding[1] = int(dim/2) + 1
        return tuple(padding)

# python prepare_training/img_scaler.py parameters/data.json 224 hyang7
def main():
    args = sys.argv
    img_scaler = ImgScaler(args[1],float(args[2]))
    img_scaler.scale(args[3])

if __name__ == "__main__":
    main()