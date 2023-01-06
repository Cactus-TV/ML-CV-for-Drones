from fastai import* 
from fastai.vision import* 
from fastai.widgets import* 
import os

def neyro(path, index):
    #print(path)
    classes = ['бетонная стена', 'кирпичная стена', 'окно', 'повреждённая бетонная стена', 'повреждённая кирпичная стена', 'разбитое окно']
    path2 = Path(os.path.dirname(__file__))
    data2 = ImageDataBunch.single_from_classes(path2, classes, ds_tfms= get_transforms(), size= 224, recompute_scale_factor=True)
    data2.normalize(imagenet_stats)
    if(index == 0):
        learn = cnn_learner( data2, models.resnet34)
        learn.load('neyro34')
    elif(index == 1):
        learn = cnn_learner( data2, models.resnet50)
        learn.load('neyro50')
    else:
        learn = cnn_learner( data2, models.resnet152)
        learn.load('neyro152')  
    img = open_image(os.path.dirname(__file__) + "\\temp\\" + path)
    #img = open_image(path)
    try:
        pred_class, pred_idx, outputs = learn.predict(img)
        return(pred_class)
    except: pass
    return('error')

