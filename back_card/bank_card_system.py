from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 模拟数据库存储
users = {}  # 存储用户信息，格式：{用户名: {密码: ..., 账户: ...}}
accounts = {}  # 存储账户信息，格式：{账户ID: {余额: ..., 状态: '正常/冻结'}}

# 1. 用户管理子系统
@app.route('/user/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return jsonify({"code": 1, "msg": "用户已存在"})
    users[username] = {"password": password, "account_id": f"acc_{username}"}
    accounts[f"acc_{username}"] = {"balance": 0, "status": "正常"}
    return jsonify({"code": 0, "msg": "注册成功"})

@app.route('/user/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username not in users or users[username]['password'] != password:
        return jsonify({"code": 1, "msg": "用户名或密码错误"})
    return jsonify({"code": 0, "msg": "登录成功", "account_id": users[username]['account_id']})

# 2. 存取款管理子系统
@app.route('/transaction/deposit', methods=['POST'])
def deposit():
    data = request.json
    account_id = data.get('account_id')
    amount = float(data.get('amount', 0))
    if account_id not in accounts or accounts[account_id]['status'] != "正常":
        return jsonify({"code": 1, "msg": "账户无效或已冻结"})
    accounts[account_id]['balance'] += amount
    return jsonify({"code": 0, "msg": "存款成功", "balance": accounts[account_id]['balance']})

@app.route('/transaction/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    account_id = data.get('account_id')
    amount = float(data.get('amount', 0))
    if account_id not in accounts or accounts[account_id]['status'] != "正常":
        return jsonify({"code": 1, "msg": "账户无效或已冻结"})
    if accounts[account_id]['balance'] < amount:
        return jsonify({"code": 1, "msg": "余额不足"})
    accounts[account_id]['balance'] -= amount
    return jsonify({"code": 0, "msg": "取款成功", "balance": accounts[account_id]['balance']})

@app.route('/transaction/query', methods=['GET'])
def query_balance():
    account_id = request.args.get('account_id')
    if account_id not in accounts:
        return jsonify({"code": 1, "msg": "账户不存在"})
    return jsonify({"code": 0, "balance": accounts[account_id]['balance']})

# 3. 账户管理子系统
@app.route('/account/lose', methods=['POST'])
def lose():
    data = request.json
    account_id = data.get('account_id')
    if account_id not in accounts:
        return jsonify({"code": 1, "msg": "账户不存在"})
    accounts[account_id]['status'] = "冻结"
    return jsonify({"code": 0, "msg": "账户已挂失（冻结）"})

@app.route('/account/close', methods=['POST'])
def close_account():
    data = request.json
    account_id = data.get('account_id')
    if account_id not in accounts:
        return jsonify({"code": 1, "msg": "账户不存在"})
    del accounts[account_id]
    # 同时删除关联用户
    for username, info in list(users.items()):
        if info['account_id'] == account_id:
            del users[username]
            break
    return jsonify({"code": 0, "msg": "账户已销户"})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 开放0.0.0.0让外部访问，端口用5000
    app.run(host='0.0.0.0', port=5000, debug=True)
