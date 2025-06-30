# this is the first and the start point of nyanlang.

The first part is just a lexer, that can lex the raw codes to tokens.(0.0.1 is for lexer completion)
I will take the llvm ir to be the front part, and use pypy to ensure it's not to embarass when talking about the speed.

Llvmlite has a lot of sh*t, and its not using typing. I just learn python >= 3.13, so I need some new features to handle the mass and big project build. (I know it just work on Numba, but it doesn't suite me.)

And I will maybe make a version on Rust in the future, But im learning, so it will take time. This project start when a  f*cking university student want to run GNU himself and its not really a good idea.

## Core Syntax
1.
// for comments
/* ... */ for multi-lines comments

2.
x: i32 // to tell compiler *hey here is a i32 named x*, and it can't be changed.
x := 5 // you give it value
x := 7 // *shallowed*, you can see this in rust, "let x = 7"
// x = 8 *Wrong!*
// also,
y: i32 := 9
// no *;*, I hate it

3.
z: ~i32 // a mut value
z = 7 // you give it value
z = 4 // you can change it
z :=8 // you cannot change it anymore!
// z becomes i32, not ~i32.
// z = 6 wrong.

4.
// you can define blocks:
add(x: i32, y: i32) -> i32
{
    ret x+y
}

//and no *def* or *func*, I hate them.

5. 
// you can define flows:
@my_flow
{
    x: i32 := 8
    y: i32 := 9
    print(x+y) // we assume there is a print just for showing the main syntax
}

// then run it 
my_flow;

// so in theory, there's no main "functions"
// you can run muiltiple flows if you like, but you need to define them
flow1;
flow2;
flow3;flow4;


6.
// use def to define custome structures
def 
{
    x: i32
    y: i32
} Point
// or 
def {x: i32, y: i32} Point
// just a refer to C typedef
C:
typedef struct {
    int x;
    int y;
} Point;
// and you also define a data type named Point when you def a struct Point.
@main
{
    P: Point := Point{4, 7}
    print(P.x)
    print(P.y)
}
main;

7.
// you can create a combining structure using block

add(x: i32, y: i32) -> i32{x: i32, y: i32}
{
    .x
    .y
    ret x+y
}

// it just return a no-name structure that has a main value i32 and a sub no-name structure {x: i32, y: i32}
// notice that you need to use the same name of the ret structure typing and the true binding value
// simp(x: i32) -> {x: i32} { y: i32 := x; .y} wrong!

@main
{
    result = add(3, 4)
    print(result) // 7
    print(result.x) // 3
    print(result.y) // 4
}
main;

8.
// control flow:
if condition {

} else {

}
// like rust, it will *return the last line*
loop
{
    xxx
}
// also ,return the last line, and you can use break to control it. break xxx will return the xxx
while xxx {
    xxxxxx
}
// as the above. 
 
// and don't forget to use continue to continue it.
// conue? ctn? go? pass? hurry? hrry? -->?==>? maybe i will think out a syntax for it. continue is much too long for me. maybe con or conue 's fine.



