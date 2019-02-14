;;; Read an analog input every second and print result

(define (analog)
  (let ((input (analog-pin (board "A0") **INPUT**))
        (output (analog-pin (board "A1") **OUTPUT**)))
    (display input) (newline)
    (display output) (newline)
    (define (loop)
      (pin-value! output (pin-value input))
      (sleep 0.5)
      (loop))
    (loop)))
