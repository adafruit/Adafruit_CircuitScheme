;;; echo a switch on pin D12 onto the onboard LED

(define (echo)
  (let ((switch (digital-pin (board "D12") **INPUT** **PULLUP**))
        (led (digital-pin (board "D13") **OUTPUT**)))
    (define (loop)
      (pin-value! led (not (pin-value? switch)))
      (loop))
    (loop)))
