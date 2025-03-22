import pygame
from byb_cars import defaults
from byb_cars.elements.layout_config import layout

# Load assets


def get_car_img():
    # return pygame.image.load(defaults.assets_dir / "assets_car.png").convert_alpha()

    car_img = pygame.image.load(defaults.assets_dir / "assets_car.png").convert_alpha()

    # Scale car image using layout config
    try:
        car_aspect_ratio = car_img.get_width() / car_img.get_height()
        car_width = int(layout.car_height * car_aspect_ratio)
        car_img = pygame.transform.scale(car_img, (car_width, layout.car_height))
    except:
        car_img = pygame.transform.scale(car_img, (layout.car_width, layout.car_height))
    return car_img


def get_tree_imgs(height):
    # Load tree images
    tree_imgs = []
    for i in range(1, 4):
        img = pygame.image.load(
                defaults.assets_dir / f"assets_tree{i}.png"
            ).convert_alpha()
        tree_imgs.append(img)

    # Scale tree images using layout config
    scaled_tree_imgs = []
    for img in tree_imgs:
        # height = layout.tree_height
        width = int(img.get_width() * (height / img.get_height()))
        scaled_tree_imgs.append(pygame.transform.scale(img, (width, height)))
    tree_imgs = scaled_tree_imgs

    return tree_imgs
