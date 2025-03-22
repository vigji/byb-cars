import pygame
from byb_cars import defaults

# Load assets


def get_car_img():
    try:
        car_img = pygame.image.load(defaults.assets_dir / "car.png").convert_alpha()
    except:
        # Create a simple car
        car_img = pygame.Surface((60, 100), pygame.SRCALPHA)
        car_img.fill((255, 0, 0))  # Red car

    # Scale car image
    car_height = 80
    car_width = 40
    try:
        car_aspect_ratio = car_img.get_width() / car_img.get_height()
        car_width = int(car_height * car_aspect_ratio)
        car_img = pygame.transform.scale(car_img, (car_width, car_height))
    except:
        car_img = pygame.transform.scale(car_img, (car_width, car_height))
    return car_img


def get_tree_imgs():
    # Load tree images
    tree_imgs = []
    for i in range(1, 4):
        try:
            img = pygame.image.load(
                defaults.assets_dir / f"tree{i}.png"
            ).convert_alpha()
            tree_imgs.append(img)
        except:
            print(f"Could not load tree{i}.png")

    # If no tree images were loaded, use a default
    if not tree_imgs:
        default_tree = pygame.Surface((60, 100), pygame.SRCALPHA)
        default_tree.fill((0, 0, 0, 0))  # Transparent
        pygame.draw.rect(default_tree, (101, 67, 33), (25, 50, 10, 50))  # Trunk
        pygame.draw.circle(default_tree, (0, 100, 0), (30, 30), 25)  # Leaves
        tree_imgs.append(default_tree)

    # Scale tree images
    scaled_tree_imgs = []
    for img in tree_imgs:
        height = 120
        width = int(img.get_width() * (height / img.get_height()))
        scaled_tree_imgs.append(pygame.transform.scale(img, (width, height)))
    tree_imgs = scaled_tree_imgs

    return tree_imgs
