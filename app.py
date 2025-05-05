import json, config
from flask import Flask, request, jsonify
from binance.um_futures import UMFutures  # ✅ Use Futures API

app = Flask(__name__)

# ✅ Initialize the Futures client
client = UMFutures(key=config.API_KEY, secret=config.API_SECRET)


def order(side, quantity, symbol, order_type="MARKET"):
    try:
        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        order = client.new_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
        print("order response:", order)
    except Exception as e:
        print(f"an exception occurred - {e}")
        return False

    return order


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    print(data['ticker'])
    print(data['bar'])

    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']  # Get quantity from the webhook data

    

    # ✅ Use correct Futures symbol — no `.P`, `.PERP`, etc.
    order_response = order(side, quantity, "BTCUSDC")

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")
        return {
            "code": "error",
            "message": "order failed"
        }


if __name__ == '__main__':
    app.run(debug=True)
