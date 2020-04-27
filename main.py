import rye

code = '''
(fun for it s e expr
    (do
        (eset it 's)
        (repeat (- 'e 's)
            (do-n 0
                (eval expr)
                (eset it (+ 'it 1))
            )
        )
    )
) 

(fun fact n
    (do 
        (set r 1)
        (for i 1 (+ 'n 1) (set r (* r i)))
        (ret r)
    )
)

(fun prime n (all (for i 2 'n (% 'n i))))

(print (fact 100))
(print (prime 13))
'''

rye.evaluate(code)