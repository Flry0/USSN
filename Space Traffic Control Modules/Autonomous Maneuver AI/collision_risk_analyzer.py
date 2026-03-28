import math

def calculate_collision_p(obj1_pos, obj2_pos, obj1_v, obj2_v):
    distance = math.sqrt((obj1_pos[0]-obj2_pos[0])**2 + (obj1_pos[1]-obj2_pos[1])**2)
    relative_v = math.sqrt((obj1_v[0]-obj2_v[0])**2 + (obj1_v[1]-obj2_v[1])**2)
    if distance < 1.0: return 1.0
    return min(1.0, relative_v / (distance * 10))

if __name__ == "__main__":
    p = calculate_collision_p([0,0], [1,1], [7.5, 0], [0, 7.5])
    print(f"Carpisma Olasiligi: %{p*100}")
