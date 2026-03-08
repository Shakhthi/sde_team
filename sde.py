import gradio as gr
from output.accounts import Account, get_share_price

demo = Account("user1", 0.0)

def create_account(initial_deposit):
    global demo
    demo = Account("user1", initial_deposit)
    return "Account created with initial deposit of " + str(initial_deposit)

def deposit(amount):
    try:
        demo.deposit(amount)
        return "Deposit successful. New balance: " + str(demo.balance)
    except Exception as e:
        return "Error: " + str(e)

def withdraw(amount):
    try:
        demo.withdraw(amount)
        return "Withdrawal successful. New balance: " + str(demo.balance)
    except Exception as e:
        return "Error: " + str(e)

def buy_shares(symbol, quantity):
    try:
        demo.buy(symbol, quantity)
        return "Shares bought successfully. New holdings: " + str(demo.holdings)
    except Exception as e:
        return "Error: " + str(e)

def sell_shares(symbol, quantity):
    try:
        demo.sell(symbol, quantity)
        return "Shares sold successfully. New holdings: " + str(demo.holdings)
    except Exception as e:
        return "Error: " + str(e)

def get_balance():
    return "Current balance: " + str(demo.balance)

def get_holdings():
    return "Current holdings: " + str(demo.holdings)

def get_portfolio_value():
    return "Current portfolio value: " + str(demo.portfolio_value())

def get_profit_loss():
    return "Current profit/loss: " + str(demo.profit_loss())

def get_transactions():
    if not demo.transactions:
        return "No transactions yet."
    
    lines = ["## Transaction History\n"]
    for tx in demo.transactions:
        date_str = tx.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if tx.type in ["deposit", "withdraw"]:
            amount_str = f"${tx.cash_amount:+.2f}"
            lines.append(f"- **{date_str}** | {tx.type.capitalize()} | {amount_str} | {tx.description}")
        else:  # buy or sell
            qty_str = f"{tx.quantity} {tx.symbol}"
            price_str = f"@ ${tx.price_per_share:.2f}" if tx.price_per_share else ""
            amount_str = f"${tx.cash_amount:+.2f}"
            lines.append(f"- **{date_str}** | {tx.type.capitalize()} | {qty_str} {price_str} | {amount_str} | {tx.description}")
    
    return "\n".join(lines)

demo_app = gr.Blocks()

with demo_app:
    gr.Markdown("# Advanced Account Management System")

    with gr.Tab("Account"):
        gr.Button("Create Account").click(create_account, inputs=[gr.Number(label="Initial Deposit")], outputs=[gr.Textbox(label="Result")])

    with gr.Tab("Deposit/Withdraw"):
        with gr.Column():
            gr.Button("Deposit").click(deposit, inputs=[gr.Number(label="Amount")], outputs=[gr.Textbox(label="Result")])
            gr.Button("Withdraw").click(withdraw, inputs=[gr.Number(label="Amount")], outputs=[gr.Textbox(label="Result")])
        with gr.Column():
            gr.Button("Get Balance").click(get_balance, outputs=[gr.Textbox(label="Result")])

    with gr.Tab("Buy/Sell Shares"):
        with gr.Column():
            gr.Button("Buy Shares").click(buy_shares, inputs=[gr.Textbox(label="Symbol"), gr.Number(label="Quantity")], outputs=[gr.Textbox(label="Result")])
            gr.Button("Sell Shares").click(sell_shares, inputs=[gr.Textbox(label="Symbol"), gr.Number(label="Quantity")], outputs=[gr.Textbox(label="Result")])
        with gr.Column():
            gr.Button("Get Holdings").click(get_holdings, outputs=[gr.Textbox(label="Result")])

    with gr.Tab("Portfolio"):
        with gr.Column():
            gr.Button("Get Portfolio Value").click(get_portfolio_value, outputs=[gr.Textbox(label="Result")])
            gr.Button("Get Profit/Loss").click(get_profit_loss, outputs=[gr.Textbox(label="Result")])
        with gr.Column():
            gr.Button("Get Transactions").click(get_transactions, outputs=[gr.Textbox(label="Result")])

if __name__ == "__main__":
    demo_app.launch()
