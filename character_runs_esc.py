from pico2d import *

open_canvas()
grass = load_image('grass.png')
character = load_image('animation_sheet.png')


# fill here





def handle_events():
    # fill here
    global running  # 지역, 전역변수를 똑같이 만들어줌
    global x

    
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:  # 윈도우 종료시 발생
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                x += 10
            elif event.key == SDLK_LEFT:
                x -= 10
            elif event.key == SDLK_ESCAPE:
                running = False

    pass


running = True
x = 800 //2
frame =0
dir=0

while running:
    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 100, 100, 100, x, 90)
    update_canvas()

    handle_events()

    frame = (frame + 1) % 8
    x+= dir * 5

    delay(0.05)


frame = 0
for x in range(0, 800, 5):

    clear_canvas()
    grass.draw(400, 30)
    character.clip_draw(frame * 100, 100, 100, 100, x, 90)
    update_canvas()

    # fill here



    frame = (frame + 1) % 8
    delay(0.05)


close_canvas()
