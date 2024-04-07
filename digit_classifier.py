import streamlit as st
import tensorflow as tf
import numpy as np

from PIL import Image
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model


def train_and_save_model():
    # load the dataset
    mnist = tf.keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    num_classes = 10
    input_shape = (28, 28, 1)

    # preprocess the data
    x_train = x_train.astype("float32") / 255
    x_test = x_test.astype("float32") / 255

    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)
    y_train = tf.keras.utils.to_categorical(y_train, num_classes)
    y_test = tf.keras.utils.to_categorical(y_test, num_classes)

    # create the model
    model = tf.keras.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(128, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"],
    )

    # train the model
    model.fit(x_train, y_train, batch_size=1000, epochs=10, validation_split=0.1)

    # evaluate the model
    model.evaluate(x_test, y_test)

    # save the model
    model.save("mnist_model.h5")


def streamlit_app():
    st.set_page_config(page_title="Digit Classifier")
    st.title("Digit Classifier")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=False)
        st.write("")

        # Preprocess the image
        image_array = np.array(image)
        if image_array.shape[2] == 4:
            # If the image has an alpha layer, extract it and resize it
            alpha_layer = image_array[:, :, 3]
            alpha_layer = Image.fromarray(alpha_layer).resize((28, 28))
            alpha_layer = img_to_array(alpha_layer)
            alpha_layer = alpha_layer.reshape(1, 28, 28, 1)

            # Normalize the alpha layer
            alpha_layer = alpha_layer.astype("float32") / 255
            image = alpha_layer

        # Load the model
        model = load_model("mnist_model.h5")

        # Use the model to make a prediction
        prediction = model.predict(image)
        predicted_class = np.argmax(prediction)

        st.write(f"Predicted digit: {predicted_class}")


# train_and_save_model()
streamlit_app()
