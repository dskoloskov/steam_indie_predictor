import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

def train_model():
    print("загружаем очищенный датасет...")
    df = pd.read_csv("data/processed/steam_cleaned.csv")
    
    # выкидываем текстовые колонки и старый таргет, оставляем только фичи (цифры)
    X = df.drop(columns=['name', 'recommendations_total', 'is_hit'])
    y = df['is_hit']
    
    print("бьем данные на тренировку (80%) и тест (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("обучаем случайный лес (random forest)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print("делаем предсказания на тестовой выборке...")
    preds = model.predict(X_test)
    
    print("\n--- результаты модели ---")
    print(classification_report(y_test, preds, zero_division=0))
    
    print("\nсохраняем модель для телеграм-бота...")
    # создаем папку, если её нет
    os.makedirs("data/models", exist_ok=True)
    
    # сохраняем саму модель
    joblib.dump(model, "data/models/rf_model.pkl")
    # сохраняем названия колонок
    joblib.dump(X.columns.tolist(), "data/models/features.pkl")
    print("готово! файлы rf_model.pkl и features.pkl лежат в data/models/")

if __name__ == "__main__":
    train_model()