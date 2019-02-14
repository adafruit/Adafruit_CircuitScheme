;;; Blink the onboard LED

(define (blink)
  (let ((led (digital-pin (board "D13") **OUTPUT**)))
    (define (loop val)
      (pin-value! led val)
      (sleep 0.5)
      (loop (not val)))
    (loop #t)))
