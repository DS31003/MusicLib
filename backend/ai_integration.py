import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np



class AlbumNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)


class AlbumImageClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(128 * 28 * 28, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


class AlbumLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        output = self.fc(last_hidden)
        return self.sigmoid(output)


class AlbumAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 4)
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, 3)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


def ucitaj_model():
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model = AlbumNet().to(device)
    try:
        model.load_state_dict(torch.load('album_model.pt', map_location=device))
        model.eval()
        return model, device
    except:
        return None, device


def izracunaj_ai_score(album):
    model, device = ucitaj_model()
    if model is None:
        return None
    
    X = torch.tensor([[
        album.godina,
        album.broj_pjesama,
        album.trajanje_min
    ]], dtype=torch.float32).to(device)
    
    with torch.no_grad():
        score = model(X).item()
    
    return round(score * 100, 1)


def klasificiraj_omot(image_path):
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model = AlbumImageClassifier().to(device)
    
    try:
        model.load_state_dict(torch.load('album_image_model.pt', map_location=device))
        model.eval()
    except:
        return None
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        score = model(image).item()
    
    return round(score * 100, 1)


def pronadi_slicne_albume(album, top_n=5):
    from albumi.models import Album
    
    svi_albumi = Album.objects.exclude(pk=album.pk)
    album_score = izracunaj_ai_score(album)
    
    slicni = []
    for a in svi_albumi:
        score = izracunaj_ai_score(a)
        razlika = abs(album_score - score)
        if razlika < 15:
            slicni.append((a, razlika))
    
    slicni.sort(key=lambda x: x[1])
    return [a for a, _ in slicni[:top_n]]


def pronadi_neobicne_albume():
    from albumi.models import Album
    
    albumi = Album.objects.all()
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model = AlbumAutoencoder().to(device)
    
    try:
        model.load_state_dict(torch.load('album_autoencoder.pt', map_location=device))
        model.eval()
    except:
        return []
    
    neobicni = []
    
    for album in albumi:
        X = torch.tensor([[
            album.godina,
            album.broj_pjesama,
            album.trajanje_min
        ]], dtype=torch.float32).to(device)
        
        with torch.no_grad():
            output = model(X)
            reconstruction_error = nn.MSELoss()(output, X).item()
        
        if reconstruction_error > 0.5:
            neobicni.append((album, reconstruction_error))
    
    neobicni.sort(key=lambda x: x[1], reverse=True)
    return neobicni[:5]


def object_detection_clustering():
    from albumi.models import Album
    
    albumi = Album.objects.all()
    
    X = np.array([[
        a.godina,
        a.broj_pjesama,
        a.trajanje_min
    ] for a in albumi])
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    clustering = DBSCAN(eps=0.5, min_samples=2).fit(X_scaled)
    
    labels = clustering.labels_
    
    grupe = {}
    for album, label in zip(albumi, labels):
        if label not in grupe:
            grupe[label] = []
        grupe[label].append(album)
    
    return grupe