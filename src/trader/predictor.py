import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class PricePredictor:
    """ML model to predict price direction"""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
    
    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training"""
        df = data.copy()
        
        df["Returns"] = df["Close"].pct_change()
        df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        
        df = df.dropna()
        
        self.feature_columns = ["RSI", "MACD", "MACD_Signal", "SMA_20", "Returns"]
        available_cols = [c for c in self.feature_columns if c in df.columns]
        
        X = df[available_cols].values
        y = df["Target"].values
        
        return X, y
    
    def train(self, data: pd.DataFrame) -> None:
        """Train the prediction model"""
        X, y = self.prepare_features(data)
        
        if len(X) < 50:
            raise ValueError("Not enough data for training")
        
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        self.model.fit(X_scaled, y)
    
    def predict(self, data: pd.DataFrame) -> Dict[str, any]:
        """Predict price direction"""
        if self.model is None:
            return {"direction": "neutral", "confidence": 0, "error": "Model not trained"}
        
        X, _ = self.prepare_features(data)
        X_scaled = self.scaler.transform(X[-1:])
        
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        direction = "up" if prediction == 1 else "down"
        confidence = float(max(probabilities)) * 100
        
        return {
            "direction": direction,
            "confidence": confidence,
            "model": self.model_type
        }
    
    def backtest(self, data: pd.DataFrame, train_size: float = 0.8) -> Dict[str, any]:
        """Backtest the model"""
        df = data.copy()
        train_data = df.iloc[:int(len(df) * train_size)]
        test_data = df.iloc[int(len(df) * train_size):]
        
        self.train(train_data)
        
        correct = 0
        total = 0
        
        for i in range(len(test_data) - 1):
            window = test_data.iloc[:i+1]
            if len(window) > 10:
                try:
                    pred = self.predict(window)
                    actual = "up" if test_data.iloc[i+1]["Close"] > test_data.iloc[i]["Close"] else "down"
                    if pred["direction"] == actual:
                        correct += 1
                    total += 1
                except:
                    pass
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "accuracy": accuracy,
            "total_predictions": total,
            "correct_predictions": correct
        }
