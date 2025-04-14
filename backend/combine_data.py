# backend/combine_data.py
from process_level2 import process_level2  # Add this import
from process_level3 import process_level3

def combine_tornado_data(level2_file, level3_data):
    level2_points = process_level2(level2_file)
    level3_points = process_level3(level3_data)
    
    # Merge, marking source for UI
    tornadoes = []
    for pt in level2_points:
        pt['source'] = 'Level II'
        tornadoes.append(pt)
    for pt in level3_points:
        pt['source'] = 'Level III'
        tornadoes.append(pt)
    
    return tornadoes

if __name__ == '__main__':
    from fetch_level2 import fetch_latest_level2
    from fetch_level3 import fetch_level3_tvs
    l2_file = fetch_latest_level2()
    l3_data = fetch_level3_tvs()
    if l2_file and l3_data:
        print(combine_tornado_data(l2_file, l3_data))
    else:
        print("Failed to fetch radar data.")