from importt import *
# эта функция обрезает чёрный фон вокруг картинки со статистикой
def crop_background(file_name):
    im = Image.open(file_name)
    pixels = im.load()
    x, y = im.size

    left = 0
    for i in range(x):
        if max(max(pixels[i, j][:3]) for j in range(y)) == 0:
            left += 1
        else:
            break

    right = 0
    for i in range(x - 1, -1, -1):
        if max(max(pixels[i, j][:3]) for j in range(y)) == 0:
            right = i
        else:
            break

    up = 0
    for j in range(y):
        if max(max(pixels[i, j][:3]) for i in range(x)) == 0:
            up += 1
        else:
            break

    down = 0
    for j in range(y - 1, -1, -1):
        if max(max(pixels[i, j][:3]) for i in range(x)) == 0:
            down = j
        else:
            break

    im.crop((left, up, right, down)).save(file_name)

