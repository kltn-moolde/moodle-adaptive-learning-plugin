import pandas as pd
import numpy as np

# Cài đặt
n_users = 200
n_gioi = int(n_users * 0.3)  # 60
n_kha = int(n_users * 0.4)   # 80
n_yeu = n_users - n_gioi - n_kha  # 60

# Tạo data
usernames = [f"student{10000 + i}" for i in range(n_users)]
passwords = ['pass123'] * n_users
groups = (['giỏi'] * n_gioi) + (['khá'] * n_kha) + (['yếu'] * n_yeu)
np.random.shuffle(groups)  # Random phân bố

# Thêm cột email, firstname, lastname
emails = [f"{u}@email.com" for u in usernames]
firstnames = ['Student'] * n_users
lastnames = [str(10000 + i) for i in range(n_users)]

# DataFrame
df = pd.DataFrame({
    'username': usernames,
    'password': passwords,
    'email': emails,
    'firstname': firstnames,
    'lastname': lastnames,
    'group': groups
})

# Save CSV (header, no index)
df.to_csv('jmeter_simulate/users.csv', index=False, encoding='utf-8')

print(f"Tạo thành công users.csv với {n_users} users: {n_gioi} giỏi, {n_kha} khá, {n_yeu} yếu.")
print(df.head())
