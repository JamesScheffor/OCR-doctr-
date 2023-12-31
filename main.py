import cv2
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from doctr.file_utils import is_tf_available
from doctr.io import DocumentFile
from doctr.utils.visualization import visualize_page
import ssl
ssl._create_default_https_context=ssl._create_unverified_context
from doctr.file_utils import is_tf_available
from doctr.io import DocumentFile
from doctr.utils.visualization import visualize_page
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
if is_tf_available():
    import tensorflow as tf

    from backend.tensorflow import DET_ARCHS, RECO_ARCHS, forward_image, load_predictor

    if any(tf.config.experimental.list_physical_devices("gpu")):
        forward_device = tf.device("/gpu:0")
    else:
        forward_device = tf.device("/cpu:0")

def main(det_archs, reco_archs):

    st.set_page_config(layout="wide")

    st.title(" Document Text Recognition")

    st.write("\n")

    st.markdown("*Hint: click on the top-right corner of an image to enlarge it!")

    cols=st.columns((1,1,1,1))
    cols[0].subheader("Input page")
    cols[1].subheader("Segmentation heatmap")
    cols[2].subheader("OCR output")
    cols[3].subheader("Page reconstitution")

    st.sidebar.title("Document selection")

    st.set_option("deprecation.showfileUploaderEncoding", False)

    uploaded_file=st.sidebar.file_uploader("Upload files", type=["pdf", "png", "jpeg", "jpg"])
    if uploaded_file is not None:
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                doc=DocumentFile.from_pdf(uploaded_file.read())
            else:
                doc=DocumentFile.from_images(uploaded_file.read())
            page_idx=st.sidebar.selectbox("Page selection", [idx+1 for idx in range(len(doc))])-1
            page=doc[page_idx]
            cols[0].image(page)

    
    st.sidebar.title("Model selection")
    st.sidebar.markdown("**Backend**:" + ("TensorFlow" if is_tf_available() else "PyTorch)"))
    det_arch=st.sidebar.selectbox("Text detection model", det_archs)
    reco_arch=st.sidebar.selectbox("Text reconition model", reco_archs)

    st.sidebar.write("\n")

    if st.sidebar.button("Analyze page"):
        if uploaded_file is None:
            st.sidebar.write("please upload a document")
        
        else:
            with st.spinner("Loading model..."):
                predictor=load_predictor(det_arch, reco_arch, forward_device)

            with st.spinner("Analyzing..."):

                seg_map=forward_image(predictor, page, forward_device)
                seg_map=np.squeeze(seg_map)
                seg_map=cv2.resize(seg_map, (page.shape[1], page.shape[0]), interpolation=cv2.INTER_LINEAR)

                fig, ax=plt.subplots()
                ax.imshow(seg_map)
                ax.axis("off")
                cols[1].pyplot(fig)

                out=predictor([page])
                fig=visualize_page(out.pages[0].export(), page, interactive=False)
                cols[2].pyplot(fig)

                page_export=out.pages[0].export()
                if "rotation" not in det_arch:
                    img=out.pages[0].synthesize()
                    cols[3].image(img, clamp=True)

                st.markdown("\nHere are your analysis results in JSON format:")
                st.json(page_export)

if __name__ == "__main__":
    main(DET_ARCHS, RECO_ARCHS)
