# ai/disease_classifier.py
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json

# Get the directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set random seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# -------------------------------
# DATA LOADING AND PREPROCESSING
# -------------------------------
def load_and_preprocess_data(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Store feature columns for later reference
    feature_columns = df.drop(['patient_id', 'diagnosis'], axis=1).columns.tolist()
    
    # Extract features and target (exclude patient_id and diagnosis)
    X = df.drop(['patient_id', 'diagnosis'], axis=1)
    y = df['diagnosis']
    
    # Convert sex to numeric (M=0, F=1)
    X['sex'] = X['sex'].map({'M': 0, 'F': 1})
    
    # Encode the target variable
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split the data into training, validation, and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.1, random_state=42, stratify=y_train
    )
    
    # Scale the numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    return (
        X_train_scaled, X_val_scaled, X_test_scaled,
        y_train, y_val, y_test,
        scaler, label_encoder, feature_columns
    )

# -------------------------------
# DATASET DEFINITION
# -------------------------------
class DiseaseDataset(Dataset):
    def __init__(self, features, labels):
        self.features = torch.tensor(features, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)
        
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]

# -------------------------------
# MODEL DEFINITION
# -------------------------------
class DiseaseClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(DiseaseClassifier, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.layer2 = nn.Linear(hidden_size, hidden_size // 2)
        self.layer3 = nn.Linear(hidden_size // 2, num_classes)
        
    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.layer2(x)
        x = self.relu(x)
        x = self.layer3(x)
        return x
    
    def predict(self, x):
        with torch.no_grad():
            outputs = self.forward(x)
            probabilities = torch.softmax(outputs, dim=1)
        return probabilities

# -------------------------------
# TRAINING FUNCTION
# -------------------------------
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=100):
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100 * correct / total
        train_losses.append(epoch_loss)
        train_accuracies.append(epoch_acc)
        
        # Validation phase
        model.eval()
        val_running_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_epoch_loss = val_running_loss / len(val_loader)
        val_epoch_acc = 100 * val_correct / val_total
        val_losses.append(val_epoch_loss)
        val_accuracies.append(val_epoch_acc)
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1}/{num_epochs}, '
                  f'Train Loss: {epoch_loss:.4f}, Train Acc: {epoch_acc:.2f}%, '
                  f'Val Loss: {val_epoch_loss:.4f}, Val Acc: {val_epoch_acc:.2f}%')
    
    return train_losses, val_losses, train_accuracies, val_accuracies

# -------------------------------
# MODEL SAVING FUNCTION (UPDATED PATHS)
# -------------------------------
def save_model(model, scaler, label_encoder, feature_columns, input_size, hidden_size, num_classes):
    # Save model checkpoint
    model_path = os.path.join(BASE_DIR, 'disease_classifier_model.pth')
    torch.save({
        'state_dict': model.state_dict(),
        'input_size': input_size,
        'hidden_size': hidden_size,
        'num_classes': num_classes
    }, model_path)
    
    # Save preprocessing artifacts
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    label_encoder_path = os.path.join(BASE_DIR, 'label_encoder.pkl')
    with open(label_encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    
    feature_columns_path = os.path.join(BASE_DIR, 'feature_columns.json')
    with open(feature_columns_path, 'w') as f:
        json.dump(feature_columns, f)

# -------------------------------
# MODEL LOADING FUNCTION (UPDATED PATHS)
# -------------------------------
def load_model_and_artifacts():
    # Load model
    model_path = os.path.join(BASE_DIR, 'disease_classifier_model.pth')
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    
    # Recreate model architecture
    model = DiseaseClassifier(
        input_size=checkpoint['input_size'],
        hidden_size=checkpoint['hidden_size'],
        num_classes=checkpoint['num_classes']
    )
    model.load_state_dict(checkpoint['state_dict'])
    
    # Load scaler
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # Load label encoder
    label_encoder_path = os.path.join(BASE_DIR, 'label_encoder.pkl')
    with open(label_encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)
    
    # Load feature columns
    feature_columns_path = os.path.join(BASE_DIR, 'feature_columns.json')
    with open(feature_columns_path, 'r') as f:
        feature_columns = json.load(f)
    
    return model, scaler, label_encoder, feature_columns

# -------------------------------
# PREDICTION FUNCTION FOR API
# -------------------------------
def predict_disease_api(model, scaler, label_encoder, feature_columns, input_data):
    # Create DataFrame with correct feature order
    input_df = pd.DataFrame([input_data], columns=feature_columns)
    
    # Preprocess sex feature
    input_df['sex'] = input_df['sex'].map({'M': 0, 'F': 1}).fillna(0)
    
    # Scale features
    scaled_data = scaler.transform(input_df)
    
    # Convert to tensor
    input_tensor = torch.tensor(scaled_data, dtype=torch.float32)
    
    # Get predictions
    with torch.no_grad():
        probabilities = model.predict(input_tensor)
    
    # Process output
    class_names = label_encoder.classes_
    probabilities = probabilities.numpy()[0]
    confidence_scores = {class_names[i]: float(probabilities[i]) for i in range(len(class_names))}
    predicted_class = class_names[np.argmax(probabilities)]
    
    return {
        'predicted_disease': predicted_class,
        'confidence_scores': confidence_scores
    }

# -------------------------------
# MAIN TRAINING EXECUTION
# -------------------------------
def main(file_path='disease_dataset.csv'):
    # Load and preprocess data
    (X_train, X_val, X_test,
     y_train, y_val, y_test,
     scaler, label_encoder, feature_columns) = load_and_preprocess_data(file_path)
    
    print(f"Classes: {label_encoder.classes_}")
    print(f"Training samples: {len(y_train)}, Validation samples: {len(y_val)}, Testing samples: {len(y_test)}")
    
    # Create datasets
    train_dataset = DiseaseDataset(X_train, y_train)
    val_dataset = DiseaseDataset(X_val, y_val)
    test_dataset = DiseaseDataset(X_test, y_test)
    
    # Create data loaders
    batch_size = 8
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Model parameters
    input_size = X_train.shape[1]
    hidden_size = 64
    num_classes = len(label_encoder.classes_)
    
    # Initialize model
    model = DiseaseClassifier(input_size, hidden_size, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Train model
    print("Starting training...")
    train_losses, val_losses, train_accuracies, val_accuracies = train_model(
        model, train_loader, val_loader, criterion, optimizer, num_epochs=100
    )
    
    # Save model and artifacts
    save_model(model, scaler, label_encoder, feature_columns, input_size, hidden_size, num_classes)
    print("Model and artifacts saved successfully")
    
    return model

# -------------------------------
# EXAMPLE USAGE
# -------------------------------
if __name__ == "__main__":
    # Train and save model
    model = main('./disease_dataset.csv')
    
    # Load artifacts for API usage
    model, scaler, label_encoder, feature_columns = load_model_and_artifacts()
    
    # Example API-style prediction
    sample_input = {
        'age': 45, 'sex': 'F', 'fever': 1, 'sore_throat': 0, 'cough': 0, 
        'headache': 0, 'fatigue': 1, 'body_ache': 1, 'runny_nose': 0, 
        'congestion': 0, 'shortness_of_breath': 0, 'nausea': 0, 
        'vomiting': 1, 'diarrhea': 0, 'chills': 0, 'rash': 0, 
        'chest_pain': 0, 'dizziness': 0, 'swollen_lymph_nodes': 0, 
        'loss_of_appetite': 0, 'joint_pain': 0, 'abdominal_pain': 0, 
        'ear_pain': 0, 'eye_redness': 0, 'loss_of_taste': 0, 
        'loss_of_smell': 0, 'wheezing': 0, 'hoarse_voice': 0, 
        'difficulty_swallowing': 0, 'muscle_weakness': 0, 
        'night_sweats': 0, 'confusion': 0, 'rapid_breathing': 0, 
        'jaundice': 0, 'itching': 0, 'bruising': 0, 'blood_in_stool': 0, 
        'weight_loss': 0, 'insomnia': 0, 'sweating': 0, 
        'symptom_duration_days': 20
    }
    
    prediction = predict_disease_api(
        model=model,
        scaler=scaler,
        label_encoder=label_encoder,
        feature_columns=feature_columns,
        input_data=sample_input
    )
    
    print("\nPrediction Result:")
    print(f"Predicted Disease: {prediction['predicted_disease']}")
    print("Confidence Scores:")
    for disease, score in prediction['confidence_scores'].items():
        print(f"{disease}: {score:.4f}")

