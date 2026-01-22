import os
import argparse
import imghdr
import pickle as pkl
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

import tensorflow as tf
from keras.applications.xception import Xception, preprocess_input
from keras.optimizers import Adam
from keras.preprocessing import image
from keras.losses import categorical_crossentropy
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model
from keras.utils import to_categorical
from keras.callbacks import ModelCheckpoint, EarlyStopping

# -----------------------
# Argument Parser
# -----------------------
parser = argparse.ArgumentParser()
parser.add_argument('dataset_root')
parser.add_argument('result_root')

parser.add_argument('--epochs_pre', type=int, default=10)
parser.add_argument('--epochs_fine', type=int, default=30)
parser.add_argument('--batch_size_pre', type=int, default=32)
parser.add_argument('--batch_size_fine', type=int, default=16)
parser.add_argument('--lr_pre', type=float, default=5e-3)
parser.add_argument('--lr_fine', type=float, default=5e-4)
parser.add_argument('--split', type=float, default=0.8)


# -----------------------
# Data Generator
# -----------------------
def generate_from_paths_and_labels(input_paths, labels, batch_size, input_size=(299, 299)):
    num_samples = len(input_paths)
    while True:
        perm = np.random.permutation(num_samples)
        input_paths = input_paths[perm]
        labels = labels[perm]
        for i in range(0, num_samples, batch_size):
            batch_paths = input_paths[i:i + batch_size]
            inputs = [image.load_img(p, target_size=input_size) for p in batch_paths]
            inputs = np.array([image.img_to_array(img) for img in inputs])
            inputs = preprocess_input(inputs)
            yield inputs, labels[i:i + batch_size]


# -----------------------
# Main Training Pipeline
# -----------------------
def main(args):

    epochs = args.epochs_pre + args.epochs_fine
    args.dataset_root = os.path.expanduser(args.dataset_root)
    args.result_root = os.path.expanduser(args.result_root)

    # Ensure results dir exists
    os.makedirs(args.result_root, exist_ok=True)

    # Classes
    classes = ['fake', 'real']
    num_classes = len(classes)

    # Collect dataset
    input_paths, labels = [], []
    for class_name in os.listdir(args.dataset_root):
        class_root = os.path.join(args.dataset_root, class_name)
        if not os.path.isdir(class_root):
            continue
        class_id = classes.index(class_name)
        for fname in os.listdir(class_root):
            path = os.path.join(class_root, fname)
            if imghdr.what(path) is None:
                continue
            input_paths.append(path)
            labels.append(class_id)

    # One-hot labels
    labels = to_categorical(labels, num_classes=num_classes)
    input_paths = np.array(input_paths)

    # Shuffle
    perm = np.random.permutation(len(input_paths))
    input_paths = input_paths[perm]
    labels = labels[perm]

    # Train/Val split
    border = int(len(input_paths) * args.split)
    train_input_paths, val_input_paths = input_paths[:border], input_paths[border:]
    train_labels, val_labels = labels[:border], labels[border:]

    print(f"Training on {len(train_input_paths)} images")
    print(f"Validating on {len(val_input_paths)} images")

    # -----------------------
    # Model
    # -----------------------
    base_model = Xception(include_top=False, weights='imagenet', input_shape=(299, 299, 3))

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.inputs, outputs=predictions)

    # -----------------------
    # Stage 1: Train top classifier
    # -----------------------
    for layer in base_model.layers:
        layer.trainable = False

    model.compile(
        loss=categorical_crossentropy,
        optimizer=Adam(learning_rate=args.lr_pre),
        metrics=['accuracy']
    )

    callbacks_pre = [
        ModelCheckpoint(
            filepath=os.path.join(args.result_root, 'model_pre_best.h5'),
            save_best_only=True,
            monitor='val_loss',
            mode='min'
        ),
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    ]

    hist_pre = model.fit(
        generate_from_paths_and_labels(train_input_paths, train_labels, args.batch_size_pre),
        steps_per_epoch=len(train_input_paths) // args.batch_size_pre,
        validation_data=generate_from_paths_and_labels(val_input_paths, val_labels, args.batch_size_pre),
        validation_steps=max(1, len(val_input_paths) // args.batch_size_pre),
        epochs=args.epochs_pre,
        callbacks=callbacks_pre,
        verbose=1
    )
    model.save(os.path.join(args.result_root, 'model_pre_final.h5'))

    # -----------------------
    # Stage 2: Fine-tuning
    # -----------------------
    for layer in model.layers:
        layer.trainable = True

    model.compile(
        loss=categorical_crossentropy,
        optimizer=Adam(learning_rate=args.lr_fine),
        metrics=['accuracy']
    )

    callbacks_fine = [
        ModelCheckpoint(
            filepath=os.path.join(args.result_root, 'model_fine_best.h5'),
            save_best_only=True,
            monitor='val_loss',
            mode='min'
        ),
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    ]

    hist_fine = model.fit(
        generate_from_paths_and_labels(train_input_paths, train_labels, args.batch_size_fine),
        steps_per_epoch=len(train_input_paths) // args.batch_size_fine,
        validation_data=generate_from_paths_and_labels(val_input_paths, val_labels, args.batch_size_fine),
        validation_steps=max(1, len(val_input_paths) // args.batch_size_fine),
        epochs=args.epochs_fine,
        callbacks=callbacks_fine,
        verbose=1
    )
    model.save(os.path.join(args.result_root, 'model_fine_final.h5'))

    # -----------------------
    # Save Training Curves
    # -----------------------
    acc = hist_pre.history['accuracy'] + hist_fine.history['accuracy']
    val_acc = hist_pre.history['val_accuracy'] + hist_fine.history['val_accuracy']
    loss = hist_pre.history['loss'] + hist_fine.history['loss']
    val_loss = hist_pre.history['val_loss'] + hist_fine.history['val_loss']

    # Accuracy plot
    plt.plot(range(epochs), acc, marker='.', label='train_acc')
    plt.plot(range(epochs), val_acc, marker='.', label='val_acc')
    plt.legend()
    plt.grid()
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.savefig(os.path.join(args.result_root, 'accuracy.png'))
    plt.clf()

    # Loss plot
    plt.plot(range(epochs), loss, marker='.', label='train_loss')
    plt.plot(range(epochs), val_loss, marker='.', label='val_loss')
    plt.legend()
    plt.grid()
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.savefig(os.path.join(args.result_root, 'loss.png'))
    plt.clf()

    # Save history
    plot = {'accuracy': acc, 'val_accuracy': val_acc, 'loss': loss, 'val_loss': val_loss}
    with open(os.path.join(args.result_root, 'plot.pkl'), 'wb') as f:
        pkl.dump(plot, f)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)