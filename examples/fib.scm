(define (fib n)
   (define (iter a b count)
     (if (<= count 0)
         a
         (iter b (+ a b) (- count 1))))
   (iter 0 1 n))

(define (fib1 n)
  (if (<= n 1)
      n
      (+ (fib1 (- n 1)) (fib1 (- n 2)))))
