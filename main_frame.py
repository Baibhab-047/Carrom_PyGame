import numpy as np

class Engine:
    def __init__(self, width, height, friction):
        self.WIDTH = width
        self.HEIGHT = height
        self.friction = friction
        self.border = self.WIDTH // 15
        self.striker_thickness = self.border // 2
        self.striker_radius = self.striker_thickness // 2
        self.coin_radius = self.border // 5
        self.radii = np.full(20, self.coin_radius)
        self.radii[19] = self.striker_radius
        self.all_pos = np.zeros((20, 2))
        self.all_vels = np.zeros((20, 2))
        self.pocket_radius = self.border * 1
        self.pockets = np.array([[self.border, self.border],
                               [self.WIDTH - self.border, self.border],
                               [self.border, self.HEIGHT - self.border],
                               [self.WIDTH - self.border, self.HEIGHT - self.border]])
        self.coins = self.all_pos[:19]
        self.striker_pos = self.all_pos[19:]
        self.coin_vels = self.all_vels[:19]
        self.striker_vel = self.all_vels[19:]
        self.rect_length = self.WIDTH // 2
        self.rect_1 = [self.WIDTH // 4, self.HEIGHT // 4 - self.striker_thickness, self.rect_length, self.striker_thickness]
        self.rect_2 = [self.WIDTH // 4, (self.HEIGHT * 3) // 4, self.rect_length, self.striker_thickness]
        self.turn = 1
        self.rect_no = None
        self.calculate_pos()
        self.color_init()

    def calculate_pos(self):
        cx, cy = self.WIDTH // 2, self.HEIGHT // 2
        res = [[cx, cy]]
        r1 = 2 * self.coin_radius + 1.5
        for a in np.linspace(0, 2 * np.pi, 6, endpoint=False):
            res.append([cx + r1 * np.cos(a), cy + r1 * np.sin(a)])
        r2 = r1 * np.sqrt(3) + 4
        for a in np.linspace(np.pi / 6, 2 * np.pi + np.pi / 6, 12, endpoint=False):
            res.append([cx + r2 * np.cos(a), cy + r2 * np.sin(a)])
        self.coins[:] = np.array(res)

    def color_init(self):
        self.queen_mask = np.zeros(19, dtype=bool)
        self.queen_mask[0] = True
        self.white_mask = np.zeros(19, dtype=bool)
        self.white_mask[1:7:2] = True
        self.white_mask[8:19:2] = True
        self.black_mask = ~(self.queen_mask | self.white_mask)

    def collision_wall(self):
        active = self.all_pos[:, 0] > 0
        hit_left = (self.all_pos[:, 0] < self.border + self.radii) & active
        hit_right = (self.all_pos[:, 0] > self.WIDTH - self.border - self.radii) & active
        hit_top = (self.all_pos[:, 1] < self.border + self.radii) & active
        hit_bottom = (self.all_pos[:, 1] > self.HEIGHT - self.border - self.radii) & active
        
        self.all_pos[hit_left, 0] = self.border + self.radii[hit_left]
        self.all_pos[hit_right, 0] = self.WIDTH - self.border - self.radii[hit_right]
        self.all_pos[hit_top, 1] = self.border + self.radii[hit_top]
        self.all_pos[hit_bottom, 1] = self.HEIGHT - self.border - self.radii[hit_bottom]
        
        self.all_vels[hit_left | hit_right, 0] *= -1
        self.all_vels[hit_top | hit_bottom, 1] *= -1

    def pieces_collision(self):
        active = (self.all_pos[:, 0] > 0)[:, np.newaxis] & (self.all_pos[:, 0] > 0)[np.newaxis, :]
        diff = self.all_pos[:, np.newaxis, :] - self.all_pos[np.newaxis, :, :]
        dist = np.linalg.norm(diff, axis=2)
        radii_sum = self.radii[:, np.newaxis] + self.radii[np.newaxis, :]
        colliding = (dist < radii_sum) & (dist > 0) & active
        if np.any(colliding):
            normals = diff / (dist[:, :, np.newaxis] + 1e-9)
            rel_vel = self.all_vels[:, np.newaxis, :] - self.all_vels[np.newaxis, :, :]
            vel_along_normal = np.sum(rel_vel * normals, axis=2)
            hit_mask = colliding & (vel_along_normal < 0)
            if np.any(hit_mask):
                mass = np.ones(20)
                mass[19] = 1.5
                m_sum = mass[:, np.newaxis] + mass[np.newaxis, :]
                indices = np.argwhere(np.triu(hit_mask))
                for i, j in indices:
                    v_rel = vel_along_normal[i, j]
                    impulse_mag = (2 * v_rel) / m_sum[i, j]
                    impulse_vec = impulse_mag * normals[i, j]
                    self.all_vels[i] -= impulse_vec * mass[j]
                    self.all_vels[j] += impulse_vec * mass[i]
                    overlap = radii_sum[i, j] - dist[i, j]
                    correction = (overlap / m_sum[i, j]) * normals[i, j]
                    self.all_pos[i] += correction * mass[j]
                    self.all_pos[j] -= correction * mass[i]

    def pocketed(self):
        active = self.all_pos[:, 0] > 0
        diff = self.all_pos[:, np.newaxis, :] - self.pockets[np.newaxis, :, :]
        dists = np.linalg.norm(diff, axis=2)
        is_pocketed = np.any(dists < self.pocket_radius, axis=1) & active
        pocketed_types = []
        if np.any(is_pocketed):
            for i in np.where(is_pocketed)[0]:
                if i == 19: continue
                if i == 0: pocketed_types.append('red')
                elif self.white_mask[i]: pocketed_types.append('white')
                else: pocketed_types.append('black')
                self.all_vels[i] = 0
                self.all_pos[i] = np.array([-1000.0, -1000.0])
        return pocketed_types

    def update(self, dt):
        pocketed_this_frame = []
        sub_dt = dt / 5
        for _ in range(5):
            self.all_pos += self.all_vels * sub_dt
            speeds = np.linalg.norm(self.all_vels, axis=1, keepdims=True)
            moving = (speeds > 0.7).flatten()
            if np.any(moving):
                deceleration = self.friction * sub_dt
                new_speeds = np.maximum(0, speeds[moving] - deceleration)
                self.all_vels[moving] *= (new_speeds / (speeds[moving] + 1e-9))
            self.collision_wall()
            self.pieces_collision()
            pocketed_this_frame.extend(self.pocketed())
        return pocketed_this_frame

    def change_turn(self):
        self.rect_no = 1 if self.turn % 2 == 1 else 2
        rect = self.rect_1 if self.rect_no == 1 else self.rect_2
        self.striker_pos[0] = [rect[0] + rect[2] // 2, rect[1] + rect[3] // 2]

    def shoot(self, power, angle):
        self.striker_vel[0] = [power * np.cos(angle), power * np.sin(angle)]