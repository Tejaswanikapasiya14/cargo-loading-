from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"  # needed for session data

# -------- FRACTIONAL KNAPSACK FUNCTION -------- #
def fractional_knapsack(items, weights, profits, capacity):
    ratio = [p / w for p, w in zip(profits, weights)]
    data = sorted(zip(items, weights, profits, ratio), key=lambda x: x[3], reverse=True)

    total_profit = 0
    selected, skipped = [], []

    for item, w, p, r in data:
        if capacity == 0:
            skipped.append((item, w, p))
            continue
        if w <= capacity:
            total_profit += p
            capacity -= w
            selected.append((item, w, p, 1))
        else:
            fraction = capacity / w
            total_profit += p * fraction
            selected.append((item, w, p, round(fraction, 2)))
            capacity = 0

    

    return total_profit, selected, skipped

# -------- ROUTES -------- #
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/input', methods=['POST'])
def input_items():
    n = int(request.form['num_items'])
    capacity = float(request.form['capacity'])
    session['num_items'] = n
    session['capacity'] = capacity
    return render_template('input.html', n=n)

@app.route('/calculate', methods=['POST'])
def calculate():
    n = session.get('num_items')
    capacity = session.get('capacity')

    items = []
    weights = []
    profits = []

    for i in range(n):
        items.append(request.form[f'item_{i}'])
        weights.append(float(request.form[f'weight_{i}']))
        profits.append(float(request.form[f'profit_{i}']))

    total_profit, selected, skipped = fractional_knapsack(items, weights, profits, capacity)

    # Visualization (Selected = Green, Skipped = Red)
    plt.figure(figsize=(8, 5))
    labels = [i for i, _, _, _ in selected] + [i for i, _, _ in skipped]
    values = [p for _, _, p, _ in selected] + [p for _, _, p in skipped]
    colors = ['green'] * len(selected) + ['red'] * len(skipped)
    plt.bar(labels, values, color=colors)
    plt.xticks(rotation=45)
    plt.xlabel("Items")
    plt.ylabel("Profit")
    plt.title("Selected (Green) vs Skipped (Red) Cargo")
    plt.tight_layout()

    graph_path = os.path.join('static', 'graph.png')
    plt.savefig(graph_path)
    plt.close()

    return render_template('result.html',
                           total_profit=round(total_profit, 2),
                           selected=selected,
                           skipped=skipped,
                           graph_path=graph_path)

if __name__ == '__main__':
    app.run(debug=True)
