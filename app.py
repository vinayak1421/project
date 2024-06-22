from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from itertools import combinations

app = Flask(__name__)

def find_groups(data, target):
    result = []
    used_indices = set()
    n = len(data)
    for r in range(1, n + 1):
        for combo in combinations(enumerate(data), r):
            indices, values = zip(*combo)
            if sum(item['size'] for item in values) == target and not used_indices.intersection(indices):
                result.append([item['id'] for item in values])
                used_indices.update(indices)
    remaining = [data[i] for i in range(n) if i not in used_indices]
    return result, remaining

def group_numbers(data, target, close_min, close_max):
    exact_groups, remaining = find_groups(data, target)
    
    close_groups = []
    if remaining:
        for r in range(1, len(remaining) + 1):
            for combo in combinations(remaining, r):
                if close_min <= sum(item['size'] for item in combo) <= close_max:
                    close_groups.append([item['id'] for item in combo])
                    for item in combo:
                        remaining.remove(item)
    
    remaining_group = [item['id'] for item in remaining] if remaining else None
    
    return exact_groups, close_groups, remaining_group

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            # Explicitly convert size column to native Python int
            df['size'] = df['size'].apply(int)
            data = [{'id': row['id'], 'size': row['size']} for index, row in df.iterrows()]
            exact_groups, close_groups, remaining_group = group_numbers(data, 280, 270, 280)
            return render_template('index.html', exact_groups=exact_groups, close_groups=close_groups, remaining_group=remaining_group)
    return render_template('index.html', exact_groups=None, close_groups=None, remaining_group=None)

if __name__ == '__main__':
    app.run(debug=True)
