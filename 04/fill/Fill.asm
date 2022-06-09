// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(START) //create a pointer with the last screen row address
    @KBD    
    D=A
    @ptr
    M=D-1//now ptr equals last screen row address
    @CHECK
    0;JMP
    
(CHECK) //checks what color to make the screen 
    //if keyboard is not pressed, jump to (WHITE)
    @KBD
    D=M;
    @WHITE
    D;JEQ
    //else jump to (BLACK)
    @BLACK
    0;JMP

(WHITE) //color the screen to white
    @ptr
    D=M
    @SCREEN
    //if (ptr == SCREEN-1) return to (START)
    A=A-1
    D=D-A
    @START
    D;JEQ
    //else change the row color to white
    @ptr
    A=M
    M=0
    @ptr
    M=M-1 //decrease address by one
    @WHITE
    0;JMP //go back to (WHITE)

(BLACK) //color the screen to black
    @ptr
    D=M
    @SCREEN
    //if (ptr == SCREEN-1) return to (START)
    A=A-1
    D=D-A
    @START
    D;JEQ
    //else change the row color to black
    @ptr
    A=M
    M=-1
    @ptr
    M=M-1 //decrease address by one
    @BLACK
    0;JMP //go back to (BLACK)



    
    
    
    
    
    



    
