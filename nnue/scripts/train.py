"""Train a small NNUE-style network for chess position evaluation.

Architecture: 768 inputs → 128 hidden (ReLU) → 32 hidden (ReLU) → 1 output
Input: 768 binary features (12 piece types × 64 squares)
Output: centipawn evaluation from side-to-move perspective

Usage:
    python nnue/scripts/train.py --data nnue/data/training_data.npz [--epochs 50]
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


class DexNNUE(nn.Module):
    """Small NNUE-style evaluation network."""

    def __init__(self, input_size=768, hidden1=128, hidden2=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden1),
            nn.ReLU(),
            nn.Linear(hidden1, hidden2),
            nn.ReLU(),
            nn.Linear(hidden2, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_model(data_path: str, output_path: str, epochs: int = 50,
                batch_size: int = 4096, lr: float = 0.001,
                val_split: float = 0.1):
    """Train the NNUE model."""
    print(f"Loading data from {data_path}...")
    data = np.load(data_path)
    features = data['features']
    evals = data['evals']
    print(f"  {len(features)} positions, features shape: {features.shape}")

    # Clip extreme evals for training stability
    evals = np.clip(evals, -3000, 3000)

    # Scale evals to roughly [-1, 1] range for training, then scale back
    eval_scale = 1000.0  # 1000cp = 1.0 in training
    evals_scaled = evals / eval_scale

    # Convert to tensors
    X = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(evals_scaled, dtype=torch.float32)

    # Train/validation split
    n_val = int(len(X) * val_split)
    indices = torch.randperm(len(X))
    train_idx = indices[n_val:]
    val_idx = indices[:n_val]

    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]

    print(f"  Training: {len(X_train)}, Validation: {len(X_val)}")

    # DataLoader
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Model
    model = DexNNUE()
    param_count = sum(p.numel() for p in model.parameters())
    print(f"  Model parameters: {param_count:,}")

    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5,
                                                      factor=0.5, verbose=True)

    # Training loop
    best_val_loss = float('inf')
    start_time = time.time()

    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0
        batches = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
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
            val_pred = model(X_val)
            val_loss = criterion(val_pred, y_val).item()

            # Calculate MAE in centipawns
            val_mae_cp = (val_pred - y_val).abs().mean().item() * eval_scale

        scheduler.step(val_loss)

        elapsed = time.time() - start_time
        print(f"  Epoch {epoch+1:3d}/{epochs}: "
              f"train_loss={train_loss:.6f} val_loss={val_loss:.6f} "
              f"val_MAE={val_mae_cp:.0f}cp "
              f"lr={optimizer.param_groups[0]['lr']:.6f} "
              f"time={elapsed:.0f}s")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'model_state_dict': model.state_dict(),
                'eval_scale': eval_scale,
                'input_size': 768,
                'hidden1': 128,
                'hidden2': 32,
                'val_loss': val_loss,
                'val_mae_cp': val_mae_cp,
                'epoch': epoch + 1,
            }, output_path)
            print(f"    -> Saved best model (MAE={val_mae_cp:.0f}cp)")

    # Final stats
    total_time = time.time() - start_time
    print(f"\nTraining complete in {total_time:.0f}s")
    print(f"Best validation MAE: {val_mae_cp:.0f} centipawns")
    print(f"Model saved to {output_path}")

    return model


def export_weights(model_path: str, output_path: str):
    """Export model weights as numpy arrays for use without PyTorch."""
    checkpoint = torch.load(model_path, map_location='cpu')
    model = DexNNUE(checkpoint['input_size'],
                    checkpoint['hidden1'],
                    checkpoint['hidden2'])
    model.load_state_dict(checkpoint['model_state_dict'])

    weights = {}
    for name, param in model.named_parameters():
        weights[name] = param.detach().numpy()

    np.savez_compressed(output_path, **weights,
                        eval_scale=np.array([checkpoint['eval_scale']]))
    print(f"Exported weights to {output_path}")
    for name, arr in weights.items():
        print(f"  {name}: {arr.shape}")


def main():
    parser = argparse.ArgumentParser(description="Train Dex NNUE model")
    parser.add_argument("--data", type=str, required=True,
                        help="Path to training data (.npz)")
    parser.add_argument("--output", "-o", type=str,
                        default="nnue/models/dex_nnue.pt",
                        help="Output model path")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--export", type=str,
                        help="Export weights to numpy format (for inference without PyTorch)")
    args = parser.parse_args()

    if args.export:
        export_weights(args.data, args.export)
    else:
        model = train_model(args.data, args.output, args.epochs,
                           args.batch_size, args.lr)
        # Also export numpy weights for PyPy inference
        export_path = args.output.replace('.pt', '_weights.npz')
        export_weights(args.output, export_path)


if __name__ == "__main__":
    main()
