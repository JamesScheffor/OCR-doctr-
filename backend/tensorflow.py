import numpy as np
import tensorflow as tf

from doctr.models import ocr_predictor
from doctr.models.predictor import OCRPredictor

DET_ARCHS=["db_resnet50", "db_mobilenet_v3_large", "linknet_resnet18_rotation"]
RECO_ARCHS=["crnn_vgg16_bn", "crnn_mobilenet_v3_small", "sar_resnet31"]

def load_predictor(det_arch:str, reco_arch:str, device)->OCRPredictor:

    with device:
        predictor=ocr_predictor(
            det_arch, reco_arch, pretrained=True, assume_straight_pages=("rotation" not in det_arch)
        )
    return predictor

def forward_image(predictor:OCRPredictor, image:np.ndarray, device)->np.ndarray:

    with device:
        processed_batches=predictor.det_predictor.pre_processor([image])
        out=predictor.det_predictor.model(processed_batches[0], return_model_output=True)
        seg_map=out["out_map"]

    with tf.device("/cpu:0"):
        seg_map=tf.identity(seg_map).numpy()
    
    return seg_map