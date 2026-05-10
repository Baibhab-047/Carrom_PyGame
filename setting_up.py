import pygame
import pygame.gfxdraw
import math

pygame.init()

class Carrom:
    def __init__(self, surface, height, width):
        self.HEIGHT=height
        self.WIDTH=width
        self.BORDER=self.HEIGHT//15
        self.HOLE_CENTERS=[]
        self.BORDER_COLOR=(142, 64, 58)
        self.SURFACE=surface
        self.CENTRE=(self.WIDTH//2, self.HEIGHT//2)
        self.striker_thickness=self.BORDER//1.5
        self.rect_length=self.WIDTH//2
        self.image_bg=pygame.image.load('assets/bg.png').convert_alpha()
        self.image_border=pygame.image.load('assets/Border.png').convert_alpha()
        self.image_border=pygame.transform.smoothscale(self.image_border, (self.WIDTH, self.HEIGHT))
        self.image_bg=pygame.transform.smoothscale(self.image_bg, (self.WIDTH-(2*self.BORDER), self.HEIGHT-(2*self.BORDER)))

    def draw_board(self):
        self.SURFACE.fill('white')
        
        self.SURFACE.blit(self.image_bg, (self.BORDER, self.BORDER))
        self.HOLE_CENTERS=[(self.BORDER,self.BORDER),(self.WIDTH-self.BORDER,self.BORDER),(self.BORDER,self.HEIGHT-self.BORDER),(self.WIDTH-self.BORDER,self.HEIGHT-self.BORDER)]
        
        offset = int(self.BORDER * 1.3)
        corners = [
            (self.BORDER + offset, self.BORDER + offset),                
            (self.WIDTH - self.BORDER - offset, self.BORDER + offset),  
            (self.BORDER + offset, self.HEIGHT - self.BORDER - offset),  
            (self.WIDTH - self.BORDER - offset, self.HEIGHT - self.BORDER - offset) 
        ]
        
        arc_radius = 25 
        angle_width = 1.5 * math.pi 
        
        for i, corner in enumerate(corners):
            end_x = (corner[0] + self.CENTRE[0]) // 2
            end_y = (corner[1] + self.CENTRE[1]) // 2
            pygame.draw.line(self.SURFACE, self.BORDER_COLOR, corner, (end_x, end_y), 2)

            arc_rect = pygame.Rect(end_x - arc_radius, end_y - arc_radius, arc_radius * 2, arc_radius * 2)
            
            if i == 0: 
                start_angle = 11*math.pi/12 
            elif i == 2: 
                start_angle = 19*math.pi/12 
            elif i == 1: 
                start_angle = 5*math.pi/12 
            elif i == 3: 
                start_angle = -math.pi/12 

            pygame.draw.arc(self.SURFACE, self.BORDER_COLOR, arc_rect, start_angle, start_angle + angle_width, 1)
        
        pygame.gfxdraw.aacircle(self.SURFACE, self.CENTRE[0], self.CENTRE[1], 1, self.BORDER_COLOR)
        pygame.gfxdraw.aacircle(self.SURFACE, self.CENTRE[0], self.CENTRE[1], int(self.BORDER*2), self.BORDER_COLOR)
        
        for center in self.HOLE_CENTERS:
            pygame.gfxdraw.filled_circle(self.SURFACE, int(center[0]), int(center[1]), int(self.BORDER*1), pygame.Color(33, 35, 34))
        
        pygame.draw.rect(self.SURFACE, self.BORDER_COLOR, (self.WIDTH//4, self.HEIGHT//4-self.striker_thickness, self.rect_length, self.striker_thickness), 1)
        pygame.draw.rect(self.SURFACE, self.BORDER_COLOR, (self.WIDTH//4, (self.HEIGHT*3)//4, self.rect_length, self.striker_thickness), 1)
        pygame.draw.rect(self.SURFACE, self.BORDER_COLOR, (self.WIDTH//4-self.striker_thickness, self.HEIGHT//4, self.striker_thickness, self.rect_length), 1)
        pygame.draw.rect(self.SURFACE, self.BORDER_COLOR, ((self.WIDTH*3)//4, self.HEIGHT//4, self.striker_thickness, self.rect_length), 1)
        
        self.SURFACE.blit(self.image_border, (0, 0))