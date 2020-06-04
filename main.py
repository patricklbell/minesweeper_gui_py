import pygame, random, time, sys, pathlib
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *

# Determine script directory and set icon and sound path
path = pathlib.Path(__file__).parent.absolute()
theme_loc = path / "icons"
sound_loc = path / "sounds"

# Setup tkinter gui with title and icon
window = Tk()
window.wm_title("Minesweeper")
#window.iconbitmap(str(path / "logo.ico"))

window.geometry('250x250')

# Setup up gui for custom board size
custom_frame = Frame(window)
lbl_h = Label(custom_frame, text="Height?")
height = Entry(custom_frame, width=10)
height.insert(END, "10")
lbl_w = Label(custom_frame, text="Width?")
width = Entry(custom_frame, width=10)
width.insert(END, "10")
lbl_m = Label(custom_frame, text="How many mines?")
mines = Entry(custom_frame, width=10)
mines.insert(END, "10")
lbl_p = Label(custom_frame, text="Pixel size of square?")
pixels = Entry(custom_frame, width=10)
pixels.insert(END, "32")

# Add the gui elements to the custom frame
lbl_h.grid(row=0, column=0, pady=10, padx=10)
height.grid(row=0, column=1, pady=10, padx=10)
lbl_w.grid(row=1, column=0, pady=10, padx=10)
width.grid(row=1, column=1, pady=10, padx=10)
lbl_m.grid(row=2, column=0, pady=10, padx=10)
mines.grid(row=2, column=1, pady=10, padx=10)
lbl_p.grid(row=3, column=0, pady=10, padx=10)
pixels.grid(row=3, column=1, pady=10, padx=10)

# Construct the combobox for choosing difficulty
combo = Combobox(window)
combo['values']= ("Beginner", "Intermediate", "Expert", "Custom")
combo.current(1) #set the selected item
combo.grid(row=0, column=0, pady=10, padx=50, stick=W+E)

# Function for changing combo value
def display_custom(event):
    # If they choose the custom setting display its settings
    if combo.get() == "Custom":
        btn.grid(row=2, column=0, pady=10, padx=10)
        custom_frame.grid(row=1, column=0)
    # All other cases reset to default
    else:
        custom_frame.grid_forget()
        btn.grid(row=1, column=0, pady=10, padx=10)

# Function to export desired setting and then destroy the corresponding objects
def destroy():
    selection = combo.get()
    global size
    global num_mines
    global sqrPx

    sqrPx = int(pixels.get())
    if selection == "Custom":
        try:
            size = (max(2, int(width.get()) ), max(2, int(height.get()) ) )
            num_mines = max(0, min(size[0]*size[1] - 1, int(mines.get())) )
        except:
            size = (10, 10)
            num_mines = 10
    elif selection == "Beginner":
        tmp = random.randint(8, 10)
        size = (tmp, tmp)
        num_mines = 10
    elif selection == "Intermediate":
        size = (random.randint(15, 16), random.randint(13, 16))
        num_mines = 40
    elif selection == "Expert":
        size = (30, 16)
        num_mines = 99
    window.destroy()

# When the combobox is changed call a function to display custom menu's gui
combo.bind("<<ComboboxSelected>>", display_custom)

# Create and bind button to export settings and break event loop
btn = Button(window, text="Play!", command=destroy)
btn.grid(row=1, column=0, pady=10, padx=10)

# Enter tkinter event loop, waiting for play event
window.mainloop()

# Hides the tkinter main window since we only use it for querying from now on
Tk().wm_withdraw()

# Returns squares in a square around a center, bounded by dimensions
def get_neighbors(x, y, width, height):
    result = []
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if x+i < width and x+i >= 0 and y+j < height and y+j >= 0 and not (x+i == x and y+j == y):
                result.append([x+i, y+j])
    return result

# Square object, essentially a struct with constructor
class square:
    def __init__(self, x, y, bomb=False, flag=False, revealed=False, near=0):
        self.x = x
        self.y = y
        self.mine = bomb
        self.flag = flag
        self.rev = revealed
        self.near = near

# Flood fill algorithm for revealing squares, bounded by numbered squares
def flood_fill(square, squares):
    if square.rev == True:
        return 0

    # Stack based method due to limits on recursion depth
    stack = [square]
    while stack:
        square = stack.pop(0)
        square.rev = True
        if not square.near > 0:
            for node in get_neighbors(square.x, square.y, len(squares), len(squares[0])):
                sqr = squares[node[0]][node[1]]
                if sqr.near == 0 and not sqr.rev:
                    stack.append(sqr)

                sqr.rev = True

    return 1

# Modififed form of the flood fill for the first click, allows limited propogation through numbered squares
def gen_flood_fill(square, squares):
    stack = [square]

    while stack:
        square = stack.pop(0)
        square.rev = True
        for node in get_neighbors(square.x, square.y, len(squares), len(squares[0])):
            sqr = squares[node[0]][node[1]]
            if sqr.near == 0 and not sqr.rev:
                stack.append(sqr)

            if not sqr.mine:
                sqr.rev = True

    return 1

# Initialize the pygame windows
pygame.init()

# Set window details, dynamically determine window size
logo = pygame.transform.scale(pygame.image.load(str(theme_loc / "logo.png")), (sqrPx, sqrPx))
pygame.display.set_icon(logo)
pygame.display.set_caption("Minesweeper")
screen = pygame.display.set_mode((size[0] * sqrPx, size[1] * sqrPx))

# Load all the number squares into a list
number_img = []
for i in range(8):
    number_img.append(pygame.transform.scale(pygame.image.load(str(theme_loc / f"mine{i+1}.png")), (sqrPx, sqrPx)) )

# Load other graphics, the icon and other square states
mine_img = pygame.transform.scale(pygame.image.load(str(theme_loc / "mine.png")), (sqrPx, sqrPx))
tilebase_img = pygame.transform.scale(pygame.image.load(str(theme_loc / "tilebase.png")), (sqrPx, sqrPx))
unmarked_img = pygame.transform.scale(pygame.image.load(str(theme_loc / "unmarked.png")), (sqrPx, sqrPx))
flag_img = pygame.transform.scale(pygame.image.load(str(theme_loc / "flag.png")), (sqrPx, sqrPx))
hit_img = pygame.transform.scale(pygame.image.load(str(theme_loc / "hit.png")), (sqrPx, sqrPx))

# Load sound files
click_sound = pygame.mixer.Sound(str(sound_loc / "click.wav"))
flag_sound = pygame.mixer.Sound(str(sound_loc / "flag.wav"))
flag_sound.set_volume(0.8)
unflag_sound = pygame.mixer.Sound(str(sound_loc / "unflag.wav"))
gameOver_sound = pygame.mixer.Sound(str(sound_loc / "gameOver.ogg"))
gameOver_sound.set_volume(0.5)
gameWin_sound = pygame.mixer.Sound(str(sound_loc / "gameWin.ogg"))
gameWin_sound.set_volume(0.5)
music = str(sound_loc / "music.ogg")

# Main function
def main():
    # Play theme music on loop
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)

    # Generate 2d array of square object of board size
    squares = []
    generated = False
    for i in range(size[0]):
        temp = []
        for j in range(size[1]):
            temp.append(square(i, j))
        squares.append(temp)

    mines = []

    # Bool to control the main loop
    running = True

    # Game loop
    while running:
        # Event handling, gets all event from the event queue
        for event in pygame.event.get():
            # Mouse click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Determine square clicked and click type
                pos = pygame.mouse.get_pos()
                mouse_type = pygame.mouse.get_pressed()
                sqr = (pos[0] // sqrPx, pos[1] // sqrPx)

                # Check that click is within board
                if sqr[0] < size[0] and sqr[0] >= 0 and sqr[1] < size[1] and sqr[1] >= 0:
                    # If they right click on an unrevealed or mine mark the square as flagged
                    if mouse_type[2] and (not squares[sqr[0]][sqr[1]].rev or squares[sqr[0]][sqr[1]].mine):
                        # Play corresonding sounds base on state change
                        if squares[sqr[0]][sqr[1]].flag:
                            unflag_sound.play()
                        else:
                            flag_sound.play()

                        squares[sqr[0]][sqr[1]].flag = not squares[sqr[0]][sqr[1]].flag

                    # Left click
                    if mouse_type[0]:
                        # We generate the board here on first click so you can't immediately die
                        if not generated:
                            click_sound.play()
                            # Lazy method of generating mines, chooses random square and makes it a mine it isn't
                            while len(mines) < num_mines:
                                choosen = (random.randint(0, size[0]-1), random.randint(0, size[1]-1))
                                if choosen not in mines and not choosen == sqr:
                                    mines.append(choosen)
                                    squares[choosen[0]][choosen[1]].mine = True
                                    for i in get_neighbors(choosen[0], choosen[1], size[0], size[1]):
                                        squares[i[0]][i[1]].near += 1

                            # Perform special flood fill and set flag as generated
                            gen_flood_fill(squares[sqr[0]][sqr[1]], squares)
                            generated = True

                        # If they left click on a flag assume they want it removed
                        elif squares[sqr[0]][sqr[1]].flag:
                            squares[sqr[0]][sqr[1]].flag = False

                        # Normal case, they have clicked on an unflagged square
                        else:
                            # Check if it is a mine, if so perform game over
                            if squares[sqr[0]][sqr[1]].mine:
                                # Graphics and sound to indicate game over
                                pygame.mixer.music.fadeout(1)
                                gameOver_sound.play()
                                # Reveal each mine with a delay
                                for mine in mines:
                                    screen.blit(mine_img, (mine[0]*sqrPx, mine[1]*sqrPx))
                                    pygame.display.update()
                                    time.sleep(0.02)

                                # Reveal the mine they clicked with special image
                                screen.blit(hit_img, (sqr[0]*sqrPx, sqr[1]*sqrPx))
                                pygame.display.update()

                                # Query user with tkinter for restart
                                if messagebox.askyesno("Restart","Do you want to restart?"):
                                    main()
                                # If they exit main we want the game to end, thus no matter the response we sys exit
                                sys.exit()

                            # Flood fill reveal the board and play sound if squares were revealed
                            if flood_fill(squares[sqr[0]][sqr[1]], squares):
                                click_sound.play()


            # Quit event
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

            # Render loop, fill screen with white
            screen.fill((255, 255, 255))
            for i in squares:
                for j in i:
                    # Render each square according to their state
                    if j.flag:
                        screen.blit(flag_img, (j.x*sqrPx, j.y*sqrPx))
                    elif j.rev:
                        if j.near > 0:
                            screen.blit(number_img[j.near - 1], (j.x*sqrPx, j.y*sqrPx))
                        # Edge case for mines which have been revealed by too generous flood fill algorithm
                        elif not j.mine:
                            screen.blit(tilebase_img, (j.x*sqrPx, j.y*sqrPx))
                        else:
                            screen.blit(unmarked_img, (j.x*sqrPx, j.y*sqrPx))

                    else:
                        screen.blit(unmarked_img, (j.x*sqrPx, j.y*sqrPx))
            pygame.display.update()

            # Determine the number of squares revealed
            sm = sum([sum([int(j.rev and not j.mine) for j in i]) for i in squares])

            # If we have revealed all squares but mines we win
            if (size[0] * size[1] - sm) == num_mines:
                # Slightly altered loss sequence
                pygame.mixer.music.fadeout(1)
                gameWin_sound.play()
                for mine in mines:
                        screen.blit(mine_img, (mine[0]*sqrPx, mine[1]*sqrPx))
                        pygame.display.update()
                        time.sleep(0.02)
                if messagebox.askyesno("You Win!","Congradulations, you won!\nDo you want to restart?"):
                    main()
                sys.exit()

if __name__=="__main__":
    main()
