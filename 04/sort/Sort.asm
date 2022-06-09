// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

// Put your code here.



@i
M=-1
(OUTER) //outer loop, runs RAM[15]-1 times
    //if i = R15-1 , go to end 
    @i
    M=M+1 //i++    
    @R15
    D=M-1
    @i
    D=D-M
    @END
    D;JEQ
    //else, go to inner loop
    @j
    M=0
    @INNER
    0;JMP
    
(INNER) //inner loop, runs RAM[15]-outer-1 times
    //if j == RAM[15]-i-1 , go to outer loop
    @R15
    D=M-1
    @i
    D=D-M
    @j
    D=D-M
    @OUTER
    D;JEQ    
    //else, check if arr[j]>arr[j+1], if true go to swap
    @j
    D=M
    @R14
    A=M+D
    D=M //D=arr[j]
    A=A+1 //M=arr[j+1]
    D=D-M 
    @SWAP
    D;JLT
    //else, go to inner
    @j
    M=M+1 //j++
    @INNER
    0;JMP

(SWAP) 
    @j  
    D=M
    @R14
    A=M+D
    D=M
    @temp
    M=D //now temp = arr[j]
    @j
    D=M+1
    @R14
    A=M+D
    D=M //now D=arr[j+1]
    A=A-1 
    M=D //now arr[j]=arr[j+1]
    @R14
    D=M
    @j
    D=D+M
    D=D+1
    @jplus //holds the address of arr[j+1]
    M=D
    @temp
    D=M
    @jplus
    A=M
    M=D // now arr[j+1] = temp
    @j
    M=M+1 //j++
    @INNER
    0;JMP

(END)
    @END
    0;JMP
    
    
    
    
