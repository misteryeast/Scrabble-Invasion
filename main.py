from tkinter import *

import random

GAME_HEIGHT = 500
GAME_WIDTH = 800
NUM_LETTERS=7
INIT_Y=20
BG_COLOR="black"
INIT_SPEED = 100
ACCELLERATION=.99
LETTER_FREQUENCY_STRING="e"*12+"ai"*9+ "o"*8+"nrt"*6+"lsud"*4+"g"*3+"bcmpfhvwy"*2+"kjqxz"
LETTER_VALUES={'a': 1, 'e': 1, 'i': 1, 'o': 1, 'n': 1, 'r': 1, 't': 1, 'l': 1, 's': 1, 'u': 1,
 'd': 2, 'g': 2, 'f': 4, 'h': 4, 'v': 4, 'w': 4, 'y': 4, 'b': 3, 'c': 3, 'm': 3,
 'p': 3, 'k': 5, 'j': 8, 'x': 8, 'q': 10, 'z': 10}
ALL_WORDS=[cl.strip().lower() for cl in open('words_list.txt')]
instructions_text=["Use the letters to make words."]
instructions_text+=["The point value of each letter is shown."]
instructions_text+=["50 points bonus for using all the letters."]
instructions_text+=["To give up on finding a word, press Escape."] 
instructions_text+=["(If no word was possible, the letters will reset.\n Otherwise the game is over.)"]

window=Tk()


window.resizable(False,False)

window.title('Scrabble Invasion! By Alon Regev')

top_frame=Frame(window)
top_frame.pack()
def instructions():
	how_window=Toplevel()
	how_window.title("Instructions")
	for tx in instructions_text:
		Label(how_window,text=tx, font = ('helvetica', 20)).pack()
how_button=Button(top_frame,text="How to play",font = ('helvetica', 20),command=instructions, bg="light blue"	)
how_button.pack(side=RIGHT,padx=100)


def all_subset_words(big_word, all_words):
    all_sub_words=[]
    for word in all_words:
        if contains_letters_of(big_word, word):
             all_sub_words.append(word)
    return all_sub_words

def contains_letters_of(big_string, little_string):
    """return true if the big string contains all the letters of the little one (in any order)"""
    if little_string=="":
        return True
    else:
        letter=little_string[0]
        if letter not in big_string:
            return False
        else:
            new_little_string=little_string[1:]
            new_big_string=big_string.replace(letter,"",1)
            return contains_letters_of(new_big_string,new_little_string)  

class Game():
	def __init__(self):
		self.fleet=Fleet()
		self.score=0
		self.score_label=Label(top_frame, text = "Score:{}".format(self.score),
								font = ('helvetica', 20))
		self.score_label.pack()		
		self.ent=Entry(top_frame)
		self.ent.pack(	)
		self.ent.focus_set()
		self.speed=INIT_SPEED
		self.gameover=False
	def next_turn(self,score_label):
		board.delete(ALL)
		for i in range(NUM_LETTERS):
			board.create_text(self.fleet.x_vals[i], self.fleet.y_vals[i],
				font=('consolas',30), 
				fill='red' if self.fleet.selected_or_not[i] else 'orange',
				text=self.fleet.string_on_board[i])
			board.create_text(self.fleet.x_vals[i]+20, self.fleet.y_vals[i]+20,
				font=('consolas',12), 
				fill='red' if self.fleet.selected_or_not[i] else 'orange',
				text=LETTER_VALUES[self.fleet.string_on_board[i]])
		for i in range(NUM_LETTERS):
			self.fleet.y_vals[i]+=1
			if self.fleet.y_vals[i]>GAME_HEIGHT:
				self.game_over()
				break
		self.score_label.config(text = "Score:{}".format(self.score))		
		if self.gameover:
			self.game_over()
			return
		window.after(int(self.speed), self.next_turn, self.score_label)
	def pressed(self,c):
		if c in self.fleet.letters_available:
			i_s=[self.fleet.positions_available[i] for i, ch in enumerate(self.fleet.letters_available) if ch == c]
			i =i_s[0]
			for j in i_s:
				if self.fleet.y_vals[j]>self.fleet.y_vals[i]:
					i=j
			#i_s=[self.fleet.positions_available[self.fleet.letters_available.find(c)]]

			self.fleet.selected_or_not[i]=True
			self.fleet.string_typed+=c
			self.fleet.positions_typed+=[i]
			self.fleet.letters_available=self.fleet.letters_available.replace(c,'',1)
			self.fleet.positions_available.remove(i)
		else:
			self.ent.delete(len(self.ent.get())-1, END)

	def pressed_Backspace(self,event):
		if not self.fleet.string_typed:
			return
		i=self.fleet.positions_typed[-1]

		self.fleet.selected_or_not[i]=False
		self.fleet.string_typed=self.fleet.string_typed[:-1]
		self.fleet.positions_typed[-1:]=[]

		self.fleet.letters_available=self.fleet.string_on_board[i]+self.fleet.letters_available
		self.fleet.positions_available =[i]+self.fleet.positions_available 
		
	def pressed_Enter(self,event):
		if check_word(self.ent.get()):
			self.score+=word_score(self.ent.get())
			self.speed*=ACCELLERATION
			self.ent.delete(0,len(self.ent.get()))
			self.fleet.reset()

		else:
			pass

	def pressed_Esc(self,event):
		all_subs = sorted(all_subset_words(self.fleet.string_on_board,ALL_WORDS),key=len,reverse = True)
		if all_subs:
			self.gameover=True
			return
		else:
			self.ent.delete(0,len(self.ent.get()))
			self.fleet=Fleet()                     
	def game_over(self):
		#board.delete(ALL)
		board.create_text(board.winfo_width()/2, board.winfo_height()/2,font=('consolas',70), fill='red',text="GAME OVER",tag="gameover")
		words_possible=all_subset_words(self.fleet.string_on_board, ALL_WORDS)
		t=Text(window)
		t.insert(END,f"Subwords of {self.fleet.string_on_board}:\n"+", ".join(words_possible))
		t.config(font=('consolas',12))
		t.pack()

def word_score(word):
	return sum([LETTER_VALUES[c] for c in word])+50*(len(word)==NUM_LETTERS)

class Fleet():
	def __init__(self):
		self.x_vals=[(i+.5)*GAME_WIDTH // NUM_LETTERS for i in range(NUM_LETTERS)]
		self.y_vals=[INIT_Y]*NUM_LETTERS
		self.letters_on_board=[random.choice(LETTER_FREQUENCY_STRING) for i in range(NUM_LETTERS)]
		self.string_on_board="".join(self.letters_on_board)
		self.letters_available=self.string_on_board
		self.positions_available=list(range(NUM_LETTERS))
		self.selected_or_not=[False]*NUM_LETTERS
		self.string_typed=""
		self.positions_typed=[]

	def reset(self):
		for i in self.positions_typed:
			self.letters_on_board[i]=random.choice(LETTER_FREQUENCY_STRING)
			self.y_vals[i]=INIT_Y
			self.positions_available+=[i]
			self.selected_or_not[i]=False
		self.string_on_board="".join(self.letters_on_board)
		self.letters_available=self.string_on_board
		self.string_typed=""
		self.positions_available=list(range(NUM_LETTERS))
		self.positions_typed=[]

alphabet = [chr(value) for value in range(97, 123)]

game=Game()


board = Canvas(window,bg=BG_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
board.pack()


window.update()

game.next_turn(game.score_label)

def check_word(word):
	return word in ALL_WORDS

for c in alphabet:
	window.bind(c, lambda event,c=c: game.pressed(c))
	window.bind(c.upper(), lambda event,c=c: game.pressed(c))
window.bind('<Escape>', game.pressed_Esc)
window.bind('<Return>',game.pressed_Enter)
window.bind('<BackSpace>', game.pressed_Backspace)
window.mainloop()