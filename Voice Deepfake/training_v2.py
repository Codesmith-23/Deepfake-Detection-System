import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.models as models
import pandas as pd
import os
from tqdm import tqdm
import time

# ================= CONFIGURATION =================
CSV_PATH = "Dataset/processed_dataset.csv" 
BATCH_SIZE = 32          # If you get "Out of Memory" error, reduce to 16
EPOCHS = 15              # Deeper models need a bit more time
LEARNING_RATE = 0.0001
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# =================================================

# 1. DATA LOADER (Same as before)
class ProcessedDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        file_path = row['path']
        label = int(row['label'])
        try:
            tensor = torch.load(file_path)
            return tensor, torch.tensor(label, dtype=torch.long)
        except:
            return torch.zeros(1, 128, 128), torch.tensor(label, dtype=torch.long)

# 2. THE SUPER BRAIN (ResNet34 + LSTM)
class ResNetLSTM(nn.Module):
    def __init__(self):
        super(ResNetLSTM, self).__init__()
        
        # A. Load Pre-trained ResNet-34
        resnet = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
        
        # B. Adapt First Layer (3 Channels -> 1 Channel)
        # We average the weights of the original RGB channels to support grayscale spectrograms
        original_weights = resnet.conv1.weight.data.mean(dim=1, keepdim=True)
        resnet.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        resnet.conv1.weight.data = original_weights
        
        # C. Remove the last fully connected layer
        self.feature_extractor = nn.Sequential(*list(resnet.children())[:-2])
        
        # D. LSTM Layer
        # ResNet34 output at this stage is 512 channels
        self.lstm = nn.LSTM(input_size=512, hidden_size=256, num_layers=2, batch_first=True, dropout=0.3)
        
        # E. Final Classifier
        self.fc = nn.Linear(256, 2)

    def forward(self, x):
        # Input: [Batch, 1, 128, 128]
        
        # 1. Extract Features
        x = self.feature_extractor(x) 
        # Output: [Batch, 512, 4, 4]
        
        # 2. Prepare for LSTM (Treat Width as Time)
        # Collapse Height (average it)
        x = x.mean(dim=2) # [Batch, 512, 4]
        # Swap axes to [Batch, Time, Features]
        x = x.permute(0, 2, 1) # [Batch, 4, 512]
        
        # 3. LSTM
        self.lstm.flatten_parameters() # Optimization for GPU
        x, _ = self.lstm(x)
        # Take the last output step
        x = x[:, -1, :] 
        
        # 4. Classify
        x = self.fc(x)
        return x

# 3. TRAINING LOOP
if __name__ == "__main__":
    print(f" Powering up {DEVICE} for ResNet-LSTM Training...")
    
    # Dataset
    dataset = ProcessedDataset(CSV_PATH)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    # Dataloaders (Pin Memory speeds up CPU->GPU transfer)
    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=False, num_workers=0, pin_memory=True)
    
    # Initialize Model
    model = ResNetLSTM().to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    best_acc = 0.0

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}")
        for inputs, labels in loop:
            # MOVE DATA TO GPU
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            loop.set_postfix(loss=loss.item(), acc=100 * correct / total)

        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        print(f"   ✅ Val Acc: {val_acc:.2f}%")
        
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), "deepfake_model_resnet_lstm.pth")
            print(" Model Saved!")

    print(" Done! Best Model: deepfake_model_resnet_lstm.pth")