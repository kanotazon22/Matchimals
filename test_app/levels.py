import random

def generate_levels1():
    configs = [
        {'rows': 4, 'cols': 6, 'beans': ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow', 'bean_purple'], 'time': 60},
        {'rows': 6, 'cols': 8, 'beans': ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow', 'bean_purple', 'bean_white'], 'time': 75},
        {'rows': 8, 'cols': 10, 'beans': ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow', 'bean_purple', 'bean_white', 'bean_orange'], 'time': 90},
        {'rows': 10, 'cols': 12, 'beans': ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow', 'bean_purple', 'bean_white', 'bean_orange', 'bean_pink'], 'time': 10},
        {'rows': 10, 'cols': 15, 'beans': ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow', 'bean_purple', 'bean_white', 'bean_orange', 'bean_pink'], 'time': 125},
    ]

    levels = []
    for i, config in enumerate(configs):
        total = config['rows'] * config['cols']
        num_types = len(config['beans'])
        per = total // num_types // 2 * 2  # làm chẵn
        distribution = {b: per for b in config['beans']}
        remain = total - per * num_types
        if remain > 0:
            distribution[config['beans'][0]] += remain

        levels.append({
            'name': f"Màn {i + 1}",
            'rows': config['rows'],
            'cols': config['cols'],
            'distribution': distribution,
            'time': config['time']
        })
    return levels
    
def generate_levels2(start_level=6, end_level=10, rows=10, cols=15):
    bean_types = ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow']
    heart_types = ['heart_red', 'heart_green', 'heart_blue', 'heart_yellow', 'heart_purple', 'heart_white']

    levels = []
    total_cells = rows * cols

    for level in range(start_level, end_level + 1):
        num_hearts = min(level - start_level + 2, len(heart_types))
        used_hearts = heart_types[:num_hearts]

        distribution = {}

        bean_per = (total_cells * 2 // 3) // len(bean_types) // 2 * 2
        for b in bean_types:
            distribution[b] = bean_per

        remain = total_cells - bean_per * len(bean_types)
        heart_per = remain // len(used_hearts) // 2 * 2
        for h in used_hearts:
            distribution[h] = heart_per
            remain -= heart_per

        if remain > 0:
            distribution[used_hearts[0]] += remain

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': distribution,
            'time': 150
        })
    return levels
 
def shape_vertical_columns(rows, cols):
    coords = []
    row_block_counts = [0 for _ in range(rows)]
    used_cols = []

    possible_cols = list(range(0, cols - 1))
    random.shuffle(possible_cols)

    for col in possible_cols:
        if any(abs(col - uc) < 3 for uc in used_cols):
            continue  # quá gần cột đã dùng

        possible_rows = []
        for r in range(rows - 3):
            if all(row_block_counts[r + i] < int(cols * 0.8) for i in range(4)):
                possible_rows.append(r)

        if possible_rows:
            r = random.choice(possible_rows)
            for i in range(4):
                coords.append((r + i, col))
                row_block_counts[r + i] += 1
            used_cols.append(col)

        if len(used_cols) >= 6:
            break

    return coords
 
def shape_horizontal_rows(rows, cols, min_required=4, max_required=6):
    coords = []
    col_block_counts = [0 for _ in range(cols)]
    used_rows = []

    # Bước 1: sinh danh sách các hàng cách đều nhau (bắt đầu từ 0 → rows)
    candidate_rows = list(range(0, rows, 3))  # mỗi hàng cách 3
    random.shuffle(candidate_rows)

    for row in candidate_rows:
        if len(used_rows) >= max_required:
            break

        # Tìm cột đặt thanh ngang 4 ô
        possible_cols = []
        for c in range(cols - 3):
            if all(col_block_counts[c + i] < rows - 1 for i in range(4)):
                possible_cols.append(c)

        if possible_cols:
            c = random.choice(possible_cols)
            for i in range(4):
                coords.append((row, c + i))
                col_block_counts[c + i] += 1
            used_rows.append(row)

    # Nếu chưa đủ thì thêm lần lượt các hàng khác còn trống
    if len(used_rows) < min_required:
        for row in range(rows):
            if any(abs(row - ur) < 3 for ur in used_rows):
                continue

            for c in range(cols - 3):
                if all(col_block_counts[c + i] < rows - 1 for i in range(4)):
                    for i in range(4):
                        coords.append((row, c + i))
                        col_block_counts[c + i] += 1
                    used_rows.append(row)
                    break
            if len(used_rows) >= min_required:
                break

    return coords
 

def generate_levels3(start_level=11, end_level=15, rows=10, cols=15):
    bean_types = ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow']
    heart_types = ['heart_red', 'heart_green', 'heart_blue', 'heart_yellow']
    total_cells = rows * cols

    # Chỉ còn 3 kiểu block
    shape_patterns = [shape_vertical_columns, shape_horizontal_rows]

    levels = []
    for level in range(start_level, end_level + 1):
        shape_fn = random.choice(shape_patterns)
        shapes = shape_fn(rows, cols)

        remain_cells = total_cells - len(shapes)

        distribution = {}
        total_items = len(bean_types) + len(heart_types)
        per_item = remain_cells // total_items // 2 * 2
        for b in bean_types:
            distribution[b] = per_item
        for h in heart_types:
            distribution[h] = per_item

        remain = remain_cells - per_item * total_items
        if remain > 0:
            distribution[bean_types[0]] += remain

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': distribution,
            'shapes': shapes,
            'time': 150
        })

    return levels

def generate_levels4(start_level=16, end_level=20, rows=12, cols=18):
    total_cells = rows * cols

    bean_types = [
        'bean_red', 'bean_green', 'bean_blue', 'bean_yellow',
        'bean_purple', 'bean_white', 'bean_orange', 'bean_pink'
    ]
    heart_types = [
        'heart_red', 'heart_green', 'heart_blue', 'heart_yellow',
        'heart_purple', 'heart_white', 'heart_orange', 'heart_pink'
    ]

    all_items = bean_types + heart_types
    total_items = len(all_items)

    levels = []

    for level in range(start_level, end_level + 1):
        per_item = total_cells // total_items // 2 * 2  # chia chẵn
        distribution = {item: per_item for item in all_items}

        remain = total_cells - per_item * total_items
        if remain > 0:
            distribution[bean_types[0]] += remain  # dồn phần dư vào 1 loại

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': distribution,
            'time': 180,
            'shapes': []  # nếu bạn muốn thêm block, có thể thêm sau
        })

    return levels

def generate_levels5(start_level=21, end_level=25, rows=10, cols=15):
    total_cells = rows * cols

    bean_types = [
        'bean_red', 'bean_green', 'bean_blue', 'bean_yellow',
        'bean_purple', 'bean_white', 'bean_orange', 'bean_pink'
    ]
    heart_types = [
        'heart_red', 'heart_green', 'heart_blue', 'heart_yellow',
        'heart_purple', 'heart_white', 'heart_orange', 'heart_pink'
    ]

    normal_items = bean_types + heart_types
    total_normal_items = len(normal_items)

    candycorn_pairs = 3  # 3 cặp -> 6 viên
    candycorn_count = candycorn_pairs * 2
    normal_cells = total_cells - candycorn_count

    per_item = normal_cells // total_normal_items // 2 * 2
    distribution = {item: per_item for item in normal_items}

    remain = normal_cells - per_item * total_normal_items
    if remain > 0:
        distribution[bean_types[0]] += remain

    distribution['candycorn'] = candycorn_count

    levels = []
    for level in range(start_level, end_level + 1):
        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),  # copy để mỗi màn độc lập
            'time': 200,
            'shapes': []
        })

    return levels
    
def generate_levels6(start_level=26, end_level=30, rows=10, cols=15):
    total_cells = rows * cols  # = 150

    bean_types = ['bean_red', 'bean_green', 'bean_blue', 'bean_yellow']
    heart_types = ['heart_red', 'heart_green', 'heart_blue', 'heart_yellow']
    round_types = ['round_red', 'round_green', 'round_blue', 'round_yellow']

    all_items = bean_types + heart_types + round_types  # 12 loại
    total_items = len(all_items)  # 12

    per_item = total_cells // total_items // 2 * 2  # chia chẵn cặp
    distribution = {item: per_item for item in all_items}

    remain = total_cells - per_item * total_items
    if remain > 0:
        distribution[bean_types[0]] += remain  # dồn dư vào bean đầu

    levels = []
    for level in range(start_level, end_level + 1):
        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'time': 225,
            'shapes': []
        })

    return levels
    
def generate_levels7(start_level=31, end_level=35, rows=12, cols=18):
    total_cells = rows * cols  # = 216

    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
    types = ['bean', 'heart', 'round']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 18 loại
    total_items = len(all_items)

    levels = []
    for level in range(start_level, end_level + 1):
        candycorn_count = 8 if level >= 33 else 0
        normal_cells = total_cells - candycorn_count

        per_item = normal_cells // total_items // 2 * 2  # chia chẵn cặp
        distribution = {item: per_item for item in all_items}

        remain = normal_cells - per_item * total_items
        if remain > 0:
            distribution['bean_red'] += remain

        if candycorn_count > 0:
            distribution['candycorn'] = candycorn_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'time': 250,
            'shapes': []
        })

    return levels
    
def generate_levels8(start_level=36, end_level=40, rows=12, cols=18):
    total_cells = rows * cols  # = 216

    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
    types = ['bean', 'heart', 'round']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 18 loại
    total_items = len(all_items)

    levels = []
    for level in range(start_level, end_level + 1):
        if level in (36, 37):
            candycorn_count = 8
            bomb_count = 0
        elif level in (38, 39, 40):
            candycorn_count = 0
            bomb_count = 6  # 3 cặp
        else:
            candycorn_count = 0
            bomb_count = 0

        special_count = candycorn_count + bomb_count
        normal_cells = total_cells - special_count

        per_item = normal_cells // total_items // 2 * 2  # chia chẵn cặp
        distribution = {item: per_item for item in all_items}

        remain = normal_cells - per_item * total_items
        if remain > 0:
            distribution['bean_red'] += remain

        if candycorn_count > 0:
            distribution['candycorn'] = candycorn_count
        if bomb_count > 0:
            distribution['bomb'] = bomb_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'time': 250,
            'shapes': []
        })

    return levels
    
def generate_levels9(start_level=41, end_level=45, rows=12, cols=18):
    total_cells = rows * cols  # 216

    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
    types = ['bean', 'heart', 'round']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 18 loại
    total_items = len(all_items)

    levels = []
    for level in range(start_level, end_level + 1):
        # Xác định số lượng đặc biệt theo level
        if level in (41, 42):
            candycorn_count = 6
            bomb_count = 6
            rainbow_count = 0
        elif level in (43, 44, 45):
            candycorn_count = 0
            bomb_count = 0
            rainbow_count = 10
        else:
            candycorn_count = bomb_count = rainbow_count = 0

        special_count = candycorn_count + bomb_count + rainbow_count
        normal_cells = total_cells - special_count

        # Phân phối item thường
        per_item = normal_cells // total_items // 2 * 2  # chia chẵn cặp
        distribution = {item: per_item for item in all_items}
        remain = normal_cells - per_item * total_items
        if remain > 0:
            distribution['bean_red'] += remain  # thêm phần dư

        # Thêm item đặc biệt
        if candycorn_count > 0:
            distribution['candycorn'] = candycorn_count
        if bomb_count > 0:
            distribution['bomb'] = bomb_count
        if rainbow_count > 0:
            distribution['rainbow'] = rainbow_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'time': 250,
            'shapes': []
        })

    return levels
    
def generate_levels10(start_level=46, end_level=50, rows=12, cols=18):
    total_cells = rows * cols  # 216

    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
    types = ['bean', 'heart', 'round']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 18 loại
    total_items = len(all_items)

    candycorn_count = 10
    bomb_count = 10
    rainbow_count = 10
    special_count = candycorn_count + bomb_count + rainbow_count  # 30
    normal_cells = total_cells - special_count  # 186

    levels = []
    for level in range(start_level, end_level + 1):
        per_item = normal_cells // total_items // 2 * 2  # chia chẵn cặp
        distribution = {item: per_item for item in all_items}
        remain = normal_cells - per_item * total_items
        if remain > 0:
            distribution['bean_red'] += remain
        distribution['candycorn'] = candycorn_count
        distribution['bomb'] = bomb_count
        distribution['rainbow'] = rainbow_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'time': 250,
            'shapes': []
        })

    return levels
    
def generate_levels11(start_level=51, end_level=55, rows=12, cols=18):
    total_cells = rows * cols  # 216

    colors = ['red', 'green', 'blue', 'yellow', 'purple',]
    types = ['bean', 'heart', 'round']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 18 loại
    total_items = len(all_items)

    candycorn_count = 10
    bomb_count = 10
    rainbow_count = 10
    special_count = candycorn_count + bomb_count + rainbow_count  # 30

    shape_patterns = [shape_vertical_columns, shape_horizontal_rows]

    levels = []
    for level in range(start_level, end_level + 1):
        # Chọn pattern và tạo block gạch chặn
        shape_fn = random.choice(shape_patterns)
        shapes = shape_fn(rows, cols)
        blocked = len(shapes)
        
        normal_cells = total_cells - special_count - blocked

        per_item = normal_cells // total_items // 2 * 2
        distribution = {item: per_item for item in all_items}
        remain = normal_cells - per_item * total_items
        if remain > 0:
            distribution['bean_red'] += remain

        # Thêm đặc biệt
        distribution['candycorn'] = candycorn_count
        distribution['bomb'] = bomb_count
        distribution['rainbow'] = rainbow_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'shapes': shapes,
            'time': 250
        })

    return levels
    
import random

def generate_levels12(start_level=56, end_level=60):
    colors = ['red', 'green', 'blue', 'yellow', 'purple']
    types = ['bean', 'heart', 'round']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 18 loại
    total_items = len(all_items)

    levels = []

    for level in range(start_level, end_level + 1):
        if level == 60:
            rows, cols = 14, 21
            total_cells = rows * cols  # 294
            special_distribution = {
                'cake': 10,
                'candycorn': 10,
                'bomb': 10,
                'rainbow': 10
            }
        else:
            rows, cols = 12, 18
            total_cells = rows * cols  # 216
            special_distribution = {
                'cake': 20
            }

        special_count = sum(special_distribution.values())
        normal_cells = total_cells - special_count

        # phân phối chẵn
        per_item = normal_cells // total_items // 2 * 2
        distribution = {item: per_item for item in all_items}

        # cộng phần dư
        remain = normal_cells - per_item * total_items
        if remain > 0:
            distribution['bean_red'] += remain

        # thêm đặc biệt
        for k, v in special_distribution.items():
            distribution[k] = v

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'shapes': [],
            'time': 250
        })

    return levels
    
def generate_levels13(start_level=61, end_level=65):
    colors = ['red', 'green', 'blue', 'yellow']
    types = ['bean', 'heart', 'round', 'jelly']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 16 loại

    levels = []
    for level in range(start_level, end_level + 1):
        rows, cols = 12, 18
        total_cells = rows * cols

        # Định nghĩa số lượng đặc biệt
        rainbow_count = 0
        bomb_count = 0
        if level in [61, 62]:
            rainbow_count = 20
        elif level in [63, 64]:
            bomb_count = 20
        elif level == 65:
            rainbow_count = 20
            bomb_count = 20

        special_count = rainbow_count + bomb_count
        normal_cells = total_cells - special_count

        # Phân phối đều các loại thường (chẵn)
        per_item = normal_cells // len(all_items) // 2 * 2
        distribution = {item: per_item for item in all_items}

        # Phân bổ phần dư nếu còn
        remain = normal_cells - per_item * len(all_items)
        if remain > 0:
            distribution['bean_red'] += remain

        # Thêm kẹo đặc biệt
        if rainbow_count > 0:
            distribution['rainbow'] = rainbow_count
        if bomb_count > 0:
            distribution['bomb'] = bomb_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': dict(distribution),
            'shapes': [],
            'time': 250
        })

    return levels

def generate_levels14(start_level=66, end_level=70):
    colors = ['red', 'green', 'blue', 'yellow']
    types = ['bean', 'heart', 'round', 'jelly']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 16 loại

    levels = []
    for level in range(start_level, end_level + 1):
        rows, cols = 12, 18
        total_cells = rows * cols

        rainbow_count = 0
        bomb_count = 0
        if level in [66, 67]:
            rainbow_count = 6  # 3 cặp
        elif level in [68, 69]:
            bomb_count = 6     # 3 cặp
        elif level == 70:
            rainbow_count = 6
            bomb_count = 6

        special_count = rainbow_count + bomb_count
        normal_cells = total_cells - special_count

        # Phân phối đều các loại thường (chẵn)
        per_item = normal_cells // len(all_items) // 2 * 2
        distribution = {item: per_item for item in all_items}

        remain = normal_cells - per_item * len(all_items)
        if remain > 0:
            distribution['bean_red'] += remain

        if rainbow_count > 0:
            distribution['rainbow'] = rainbow_count
        if bomb_count > 0:
            distribution['bomb'] = bomb_count

        # Tăng băng ~60% tổng ô
        ice_target = int(total_cells * 0.3)
        frozen = {}
        unfrozen = {}

        # Tạo pool từ distribution
        tile_pool = []
        for key, count in distribution.items():
            if key == 'block':
                continue
            tile_pool.extend([key] * count)
        random.shuffle(tile_pool)

        for i, key in enumerate(tile_pool):
            if i < ice_target:
                ice_key = f"ice_{key}"
                frozen[ice_key] = frozen.get(ice_key, 0) + 1
            else:
                unfrozen[key] = unfrozen.get(key, 0) + 1

        # Gộp
        final_distribution = {}
        final_distribution.update(unfrozen)
        for ice_key, count in frozen.items():
            final_distribution[ice_key] = final_distribution.get(ice_key, 0) + count
        if rainbow_count > 0:
            final_distribution['rainbow'] = rainbow_count
        if bomb_count > 0:
            final_distribution['bomb'] = bomb_count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': final_distribution,
            'shapes': [],
            'time': 270
        })

    return levels

def generate_levels15(start_level=71, end_level=75):
    colors = ['red', 'green', 'blue', 'yellow']
    types = ['bean', 'heart', 'round', 'jelly']
    all_items = [f"{t}_{c}" for t in types for c in colors]  # 16 loại

    levels = []
    for level in range(start_level, end_level + 1):
        rows, cols = 12, 18
        total_cells = rows * cols
        ice_target = int(total_cells * 0.5)

        # Không có kẹo đặc biệt
        per_item = total_cells // len(all_items) // 2 * 2
        distribution = {item: per_item for item in all_items}

        remain = total_cells - per_item * len(all_items)
        if remain > 0:
            distribution['bean_red'] += remain

        # Tạo danh sách tất cả các viên kẹo thường
        tile_pool = []
        for key, count in distribution.items():
            tile_pool.extend([key] * count)
        random.shuffle(tile_pool)

        frozen = {}
        unfrozen = {}

        for i, key in enumerate(tile_pool):
            if i < ice_target:
                ice_key = f"ice_{key}"
                frozen[ice_key] = frozen.get(ice_key, 0) + 1
            else:
                unfrozen[key] = unfrozen.get(key, 0) + 1

        # Gộp lại
        final_distribution = dict(unfrozen)
        for ice_key, count in frozen.items():
            final_distribution[ice_key] = final_distribution.get(ice_key, 0) + count

        levels.append({
            'name': f"Màn {level}",
            'rows': rows,
            'cols': cols,
            'distribution': final_distribution,
            'shapes': [],
            'time': 300
        })

    return levels
    
LEVELS1 = generate_levels1()
LEVELS2 = generate_levels2()
LEVELS3 = generate_levels3()
LEVELS4 = generate_levels4()
LEVELS5 = generate_levels5()
LEVELS6 = generate_levels6()
LEVELS7 = generate_levels7()
LEVELS8 = generate_levels8()
LEVELS9 = generate_levels9()
LEVELS10 = generate_levels10()
LEVELS11 = generate_levels11()
LEVELS12 = generate_levels12()
LEVELS13 = generate_levels13()
LEVELS14 = generate_levels14()
LEVELS15 = generate_levels15()
LEVELS = (
    LEVELS1 + LEVELS2 + LEVELS3 + LEVELS4 + LEVELS5 +
    LEVELS6 + LEVELS7 + LEVELS8 + LEVELS9 + LEVELS10 +
    LEVELS11 + LEVELS12 + LEVELS13 + LEVELS14 + LEVELS15
)
