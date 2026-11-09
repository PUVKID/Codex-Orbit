"""특집 주제의 앞뒤 두께와 부품을 실제 삼각형 메시로 만듭니다."""
import math
import numpy as np


def special_geometry(spec, color):
    from calendar_renderer import sphere_mesh, box, lathe, tube, _transformed, rotation
    from fruit_surface import surface_tube
    parts = []
    gold = (.65, .38, .08)
    red = (.45, .025, .045)
    cream = (.78, .70, .51)
    green = (.025, .15, .055)
    dark = (.012, .015, .02)

    def add(mesh, pos=(0, 0, 0), tint=color, metal=0., rough=.48, angle=0.):
        parts.append((_transformed(mesh, pos, angle=angle), tint, metal, rough))

    def block(size, pos, tint=color, angle=0.):
        add(box(size, min(.7, min(size)/4), 4), pos, tint, angle=angle)

    def ball(pos, scale, tint=color, metal=0.):
        add(_transformed(sphere_mesh(1, 40, 24), scale=scale), pos, tint, metal)

    def stroke(points, radius=1.4, tint=color):
        add(surface_tube(points, radius, False, 12), tint=tint)

    def face(radius, depth, tint):
        mesh = lathe([(0, -depth), (radius, -depth), (radius, depth), (0, depth)], 80)
        vertices, indices = mesh
        matrix = rotation((1, 0, 0), math.pi/2)
        vertices[:, :3] = vertices[:, :3] @ matrix.T
        vertices[:, 3:] = vertices[:, 3:] @ matrix.T
        add((vertices, indices), tint=tint)

    recipe = spec.recipe
    if recipe == 'tree':
        add(lathe([(0, -34), (4, -34), (4, -18), (0, -18)], 24), tint=(.18, .065, .02))
        for tier in range(5):
            bottom = -24 + tier*10
            radius = 27-tier*4.4
            add(lathe([(0, bottom), (radius, bottom), (radius*.88, bottom+3), (0, bottom+25)], 64), tint=green)
            for j in range(10):
                t = math.tau*j/10 + tier*.4
                ball((radius*.79*math.cos(t), bottom+4, radius*.79*math.sin(t)), (1.6,)*3, red if j%2 else gold, .4)
        # 꼭대기 별의 다섯 꼭짓점은 입체 중심과 연결합니다.
        for j in range(5):
            t = math.tau*j/5 + math.pi/2
            stroke([(0, 42, 0), (6*math.cos(t), 42+6*math.sin(t), 0)], 1.5, gold)
    elif recipe in ('gift','celebration'):
        block((43, 37, 34), (0, -3, 0), red)
        block((45, 5, 36), (0, 18, 0), (.56, .04, .06))
        block((7, 40, 35), (0, -2, 0), gold)
        block((44, 40, 7), (0, -2, 0), gold)
        for side in (-1, 1):
            points = [(side*12*math.sin(t), 23+7*math.sin(t), 7*math.sin(2*t)) for t in np.linspace(0, math.pi, 40)]
            stroke(points, 1.8, gold)
        if recipe=='celebration':
            for j in range(5):
                t=math.pi*(j+.5)/5
                stroke([(27*math.cos(t),27+8*math.sin(t),0),(33*math.cos(t),27+15*math.sin(t),0)],1.2,gold)
    elif recipe == 'heart':
        vertices, indices = sphere_mesh(1, 80, 48)
        p = vertices[:, :3].copy()
        x, y, z = p.T.copy()
        p[:, 0] = x*25*(.78+.22*y)
        p[:, 1] = y*27 + 8*np.abs(x) - 5*np.exp(-(x/.18)**2)*np.maximum(y, 0)
        p[:, 2] = z*10
        # 변형 뒤 삼각형의 실제 면 법선을 합산합니다.
        ix = indices.reshape(-1, 3); tri = p[ix]
        normals = np.zeros_like(p)
        n = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
        for c in range(3): np.add.at(normals, ix[:, c], n)
        lengths = np.linalg.norm(normals, axis=1)
        missing = lengths < 1e-8
        normals[missing] = vertices[missing, 3:]
        normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-8)
        add((np.concatenate((p, normals), axis=1).astype('f4'), indices), tint=red)
    elif recipe == 'pinwheel':
        stroke([(0, -42, -3), (0, 8, -3)], 1.7, (.35, .17, .06))
        for j, tint in enumerate((red, gold, (.04, .28, .55), green)):
            angle = math.tau*j/4
            mesh = box((17, 23, 3), 1.2, 6)
            add(mesh, (12*math.cos(angle), 8+12*math.sin(angle), j*.4), tint, angle=angle+.4)
        ball((0, 8, 4), (3,)*3, gold, .6)
    elif recipe == 'pumpkin':
        # 골을 포함하는 하나의 닫힌 호박 표면입니다.
        vertices, indices = sphere_mesh(1, 96, 48)
        p = vertices[:, :3].copy(); theta = np.arctan2(p[:, 2], p[:, 0])
        radial = 1+.09*np.cos(10*theta)*(1-p[:, 1]**2)
        p[:, 0] *= radial*27; p[:, 1] *= 24; p[:, 2] *= radial*24
        normals = p/np.array((27**2, 24**2, 24**2))
        normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-8)
        add((np.concatenate((p, normals), axis=1).astype('f4'), indices), tint=(.64, .19, .012))
        stroke([(0, 23, 0), (1, 30, 0), (5, 33, 0)], 2.3, green)
        for side in (-1, 1):
            block((8, 3, 2), (side*10, 7, 23), dark, side*.4)
        for j in range(7):
            block((4, 3, 2), ((j-3)*4, -9+abs(j-3), 23), dark)
    elif recipe == 'clock':
        face(29, 3.5, gold)
        face(26, 3.7, cream)
        for j in range(12):
            t = math.tau*j/12
            block((1.2, 3.2, 1), (23*math.sin(t), 23*math.cos(t), 4.2), dark, -t)
        stroke([(0, 0, 5), (-4, 18, 5)], .9, dark)
        stroke([(0, 0, 5.2), (0, 14, 5.2)], 1.2, dark)
        ball((0, 0, 6), (2, 2, 1), gold, .6)
    elif recipe == 'new_year':
        ball((0, 5, 0), (23, 23, 8), gold)
        for j in range(9):
            t = math.pi*j/8
            stroke([(29*math.cos(t), 5+29*math.sin(t), 0), (35*math.cos(t), 5+35*math.sin(t), 0)], 1.3, gold)
        for y, width in ((-16, 30), (-23, 24), (-30, 17)):
            stroke([(-width, y, 10), (0, y+1, 11), (width, y, 10)], 1.4, (.08, .24, .35))
    elif recipe == 'hangul':
        # 두 음절의 자모 획을 앞뒤 두께가 있는 원통으로 구성합니다.
        for points in (
            [(-27, 23, 0), (-18, 23, 0)], [(-30, 18, 0), (-15, 18, 0)],
            [(-10, 22, 0), (-10, 1, 0)], [(-10, 12, 0), (-4, 12, 0)],
            [(-29, -2, 0), (-29, -12, 0), (-9, -12, 0)],
            [(5, 23, 0), (27, 23, 0), (27, 11, 0)], [(4, 4, 0), (28, 4, 0)],
            [(5, -4, 0), (27, -4, 0), (27, -11, 0), (5, -11, 0), (5, -19, 0), (28, -19, 0)],
        ): stroke(points, 1.8, cream)
        points = [(-22.5+5*math.cos(t), 9+5*math.sin(t), 0) for t in np.linspace(0, math.tau, 40)]
        stroke(points, 1.7, cream)
    else:
        raise ValueError('지원하지 않는 특집 형상: '+recipe)
    return parts
