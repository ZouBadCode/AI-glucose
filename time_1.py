from datetime import datetime, timedelta

def find_nearest_hours():
    # 獲取當前時間
    now = datetime.now()
    
    # 如果當前分鐘數為0，則前一個整點就是當前小時減去1，後一個整點就是當前小時
    if now.minute == 0:
        previous_hour = now - timedelta(hours=1)
        next_hour = now
    else:
        # 當前分鐘數不為0時，前一個整點是當前小時，後一個整點是當前小時加上1
        previous_hour = now.replace(minute=0, second=0, microsecond=0)
        next_hour = previous_hour + timedelta(hours=1)
    
    # 格式化輸出前後整點時間
    return previous_hour.strftime('%Y-%m-%d %H:%M:%S'), next_hour.strftime('%Y-%m-%d %H:%M:%S')

# 測試函式
previous_hour, next_hour = find_nearest_hours()
print("前一個整點時間:", previous_hour)
print("後一個整點時間:", next_hour)