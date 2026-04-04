"""Train a NNUE-style network for chess position evaluation.

Architecture: 768 inputs → hidden1 → hidden2 → 1 output
Training target: WDL (win/draw/loss) via sigmoid(eval/400)

Usage:
    python nnue/scripts/train.py --data nnue/data/fishtest_training_data.npz [--epochs 50]
"""

import sys
import os
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import time
import math


class DexNNUE(nn.Module):
    """NNUE-style evaluation network."""

    def __init__(self, input_size=768, hidden1=256, hidden2=64, hidden3=0):
        super().__init__()
        layers = [
            nn.Linear(input_size, hidden1),
            nn.ReLU(),
            nn.Linear(hidden1, hidden2),
            nn.ReLU(),
        ]
        if hidden3 > 0:
            layers.extend([
                nn.Linear(hidden2, hidden3),
                nn.ReLU(),
                nn.Linear(hidden3, 1),
            ])
        else:
            layers.append(nn.Linear(hidden2, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)


def cp_to_wdl(cp: np.ndarray, k: float = 400.0) -> np.ndarray:
    """Convert centipawn eval to WDL (sigmoid) in range [0, 1].
    0.0 = black wins, 0.5 = draw, 1.0 = white wins.
    """
    return 1.0 / (1.0 + np.exp(-cp / k))


def wdl_to_cp(wdl: float, k: float = 400.0) -> float:
    """Convert WDL back to centipawns."""
    wdl = max(0.001, min(0.999, wdl))
    return k * math.log(wdl / (1.0 - wdl))


def train_model(data_path: str, output_path: str, epochs: int = 50,
                batch_size: int = 4096, lr: float = 0.001,
                val_split: float = 0.1, hidden1: int = 256,
                hidden2: int = 64, hidden3: int = 0):
    """Train the NNUE model using WDL targets."""
    print(f"Loading data from {data_path}...")
    data = np.load(data_path)
    features = data['features']
    evals = data['evals']
    print(f"  {len(features)} positions, features shape: {features.shape}")

    # Clip extreme evals
    evals = np.clip(evals, -5000, 5000)

    # Convert to WDL targets (sigmoid)
    wdl_targets = cp_to_wdl(evals)
    print(f"  WDL range: [{wdl_targets.min():.4f}, {wdl_targets.max():.4f}]")
    print(f"  WDL mean: {wdl_targets.mean():.4f}")

    # Convert to tensors
    X = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(wdl_targets, dtype=torch.float32)

    # Train/validation split
    n_val = int(len(X) * val_split)
    indices = torch.randperm(len(X))
    train_idx = indices[n_val:]
    val_idx = indices[:n_val]

    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]
    # Keep original cp evals for validation MAE
    evals_val = evals[val_idx.numpy()]

    print(f"  Training: {len(X_train)}, Validation: {len(X_val)}")

    # DataLoader
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Model
    model = DexNNUE(hidden1=hidden1, hidden2=hidden2, hidden3=hidden3)
    param_count = sum(p.numel() for p in model.parameters())
    arch = f"768 → {hidden1} → {hidden2}"
    if hidden3:
        arch += f" → {hidden3}"
    print(f"  Model: {arch} → 1 ({param_count:,} params)")

    # Loss: BCE since target is sigmoid(eval)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    best_val_loss = float('inf')
    start_time = time.time()

    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0
        batches = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            # Model outputs raw logits, loss applies sigmoid internally
            pred = model(X_batch)
            loss = criterion(pred, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            batches += 1

        train_loss /= batches

        # Validate
        model.eval()
        with torch.no_grad():
            val_logits = model(X_val)
            val_loss = criterion(val_logits, y_val).item()

            # Convert predictions back to centipawns for MAE
            val_wdl = torch.sigmoid(val_logits).numpy()
            val_cp = np.array([wdl_to_cp(w) for w in val_wdl])
            val_mae_cp = np.abs(val_cp - evals_val).mean()

        scheduler.step(val_loss)

        elapsed = time.time() - start_time
        print(f"  Epoch {epoch+1:3d}/{epochs}: "
              f"train_loss={train_loss:.6f} val_loss={val_loss:.6f} "
              f"val_MAE={val_mae_cp:.0f}cp "
              f"lr={optimizer.param_groups[0]['lr']:.6f} "
              f"time={elapsed:.0f}s")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'model_state_dict': model.state_dict(),
                'input_size': 768,
                'hidden1': hidden1,
                'hidden2': hidden2,
                'hidden3': hidden3,
                'val_loss': val_loss,
                'val_mae_cp': val_mae_cp,
                'epoch': epoch + 1,
                'use_wdl': True,
            }, output_path)
            print(f"    -> Saved best model (MAE={val_mae_cp:.0f}cp)")

    total_time = time.time() - start_time
    print(f"\nTraining complete in {total_time:.0f}s")
    print(f"Model saved to {output_path}")

    return model


def export_weights(model_path: str, output_path: str):
    """Export model weights as numpy arrays for use without PyTorch."""
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
    model = DexNNUE(checkpoint['input_size'],
                    checkpoint['hidden1'],
                    checkpoint['hidden2'],
                    checkpoint.get('hidden3', 0))
    model.load_state_dict(checkpoint['model_state_dict'])

    weights = {}
    for name, param in model.named_parameters():
        weights[name] = param.detach().numpy()

    np.savez_compressed(output_path, **weights,
                        use_wdl=np.array([1 if checkpoint.get('use_wdl') else 0]))
    print(f"Exported weights to {output_path}")
    for name, arr in weights.items():
        print(f"  {name}: {arr.shape}")


def main():
    parser = argparse.ArgumentParser(description="Train Dex NNUE model")
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--output", "-o", type=str, default="nnue/models/dex_nnue.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--hidden1", type=int, default=256)
    parser.add_argument("--hidden2", type=int, default=64)
    parser.add_argument("--hidden3", type=int, default=0,
                        help="Third hidden layer size (0 = no third layer)")
    parser.add_argument("--export", type=str,
                        help="Export weights from model file")
    args = parser.parse_args()

    if args.export:
        export_weights(args.data, args.export)
    else:
        model = train_model(args.data, args.output, args.epochs,
                           args.batch_size, args.lr,
                           hidden1=args.hidden1, hidden2=args.hidden2,
                           hidden3=args.hidden3)
        export_path = args.output.replace('.pt', '_weights.npz')
        export_weights(args.output, export_path)


if __name__ == "__main__":
    main()
