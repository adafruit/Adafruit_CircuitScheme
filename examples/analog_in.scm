;;; Read an analog input every second and print result

(define (analog)
  (let ((input (analog-pin (board "A0") **INPUT**)))
    (define (loop)
      (display (pin-value input))
      (newline)
      (sleep 0.5)
      (loop))
    (loop)))
