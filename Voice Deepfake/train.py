import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
import os

# --- CONFIGURATION ---
DATA_PATH = r"C:\Users\Moinuddin's Projects\Voice Deepfake\Dataset\LA\processed_images\train"
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001
IMG_SIZE = (128, 128)

# Check for GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f" Training on device: {device}")

def main():
    # 1. Prepare Data Transforms (Resize & Convert to Tensor)
    transform = transforms.Compose([
        transforms.Resize(IMG_SIZE),
        transforms.ToTensor(),
        # Normalize roughly helps convergence (mean, std)
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)) 
    ])

    # 2. Load Dataset from Folders
    print(" Loading dataset...")
    try:
        full_dataset = ImageFolder(root=DATA_PATH, transform=transform)
    except FileNotFoundError:
        print(f" Error: Could not find folder {DATA_PATH}")
        return

    # Split: 80% for Training, 20% for Validation
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    print(f" Data Loaded: {len(full_dataset)} images")
    print(f"   - Training: {train_size}")
    print(f"   - Validation: {val_size}")
    print(f"   - Classes: {full_dataset.classes}") # Should be ['fake', 'real']

    # 3. Create DataLoaders
    # num_workers=0 is safest for Windows to avoid the "stuck at 0" freeze again
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    # 4. Define the CNN Model
    class DeepFakeCNN(nn.Module):
        def __init__(self):
            super(DeepFakeCNN, self).__init__()
            # Convolutional Block 1
            self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
            self.relu = nn.ReLU()
            self.pool = nn.MaxPool2d(2, 2)
            
            # Convolutional Block 2
            self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
            
            # Convolutional Block 3
            self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
            
            # Fully Connected Layers
            # Image is 128x128 -> pool(64) -> pool(32) -> pool(16)
            # So final feature map is 128 channels * 16 * 16 size
            self.fc1 = nn.Linear(128 * 16 * 16, 512)
            self.fc2 = nn.Linear(512, 2) # Output: 2 classes (Real vs Fake)
            self.dropout = nn.Dropout(0.5) # Prevent Overfitting

        def forward(self, x):
            x = self.pool(self.relu(self.conv1(x))) # 128 -> 64
            x = self.pool(self.relu(self.conv2(x))) # 64 -> 32
            x = self.pool(self.relu(self.conv3(x))) # 32 -> 16
            
            x = x.view(-1, 128 * 16 * 16) # Flatten
            x = self.dropout(self.relu(self.fc1(x)))
            x = self.fc2(x)
            return x

    model = DeepFakeCNN().to(device)
    
    # 5. Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 6. Training Loop
    print("\n Starting Training...")
    
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}", leave=True)
        
        for inputs, labels in loop:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Zero the gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Stats
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            loop.set_postfix(loss=loss.item(), acc=100 * correct / total)

        # Validation Step (End of Epoch)
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        print(f"    Validation Accuracy: {val_acc:.2f}%")

    # 7. Save Model
    torch.save(model.state_dict(), "deepfake_model.pth")
    print("\n Model saved as 'deepfake_model.pth'!")

if __name__ == "__main__":
    main()