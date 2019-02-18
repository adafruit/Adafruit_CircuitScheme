;;; Scheme Interpreter in CircuitPython
;;; Based on Lispy.py (c) Peter Norvig, 2010; See http://norvig.com/lispy2.html
;;;
;;; Adafruit invests time and resources providing this open source code.
;;; Please support Adafruit and open source hardware by purchasing
;;; products from Adafruit!
;;;
;;; Written by Dave Astels for Adafruit Industries
;;; Copyright (c) 2019 Adafruit Industries
;;; Licensed under the MIT license.
;;;
;;; All text above must be included in any redistribution.
;;;
;;; Lists support library
;;; Adds the rich set of standard Scheme list functions.  Only the
;;; basic list functions are builtin

(define (nth k l)
  (if (eq? k 0)
      (car l)
      (nth (- k 1) (cdr l))))

(define (list-ref l k)
  (nth k l))

;; Remove any elements of l for which p evaluates to #t

(define (remove a-predicate a-list)
  (define (inner a-predicate a-list accumulated)
    (cond ((null? a-list)
           accumulated)
          ((a-predicate (car a-list))
           (inner a-predicate (cdr a-list) accumulated))
          (#t
           (inner a-predicate (cdr a-list) (append accumulated (list (car a-list)))))))
  (inner a-predicate a-list '()))

(define (delq element l)
  (remove (lambda (x) (eq? x element)) l))

(define (delete element l)
  (remove (lambda (x) (equal? x element)) l))

(define (caar l) (car (car l)))
(define (cadr l) (car (cdr l)))
(define (cdar l) (cdr (car l)))
(define (cddr l) (cdr (cdr l)))

(define (caaar l) (car (car (car l))))
(define (caadr l) (car (car (cdr l))))
(define (cadar l) (car (cdr (car l))))
(define (caddr l) (car (cdr (cdr l))))
(define (cdaar l) (cdr (car (car l))))
(define (cdadr l) (cdr (car (cdr l))))
(define (cddar l) (cdr (cdr (car l))))
(define (cdddr l) (cdr (cdr (cdr l))))

(define (caaaar l) (cdr (car (car (car l)))))
(define (caaadr l) (cdr (car (car (cdr l)))))
(define (caadar l) (cdr (car (cdr (car l)))))
(define (caaddr l) (cdr (car (cdr (cdr l)))))
(define (cadaar l) (cdr (cdr (car (car l)))))
(define (cadadr l) (cdr (cdr (car (cdr l)))))
(define (caddar l) (cdr (cdr (cdr (car l)))))
(define (cadddr l) (cdr (cdr (cdr (cdr l)))))
(define (cdaaar l) (cdr (car (car (car l)))))
(define (cdaadr l) (cdr (car (car (cdr l)))))
(define (cdadar l) (cdr (car (cdr (car l)))))
(define (cdaddr l) (cdr (car (cdr (cdr l)))))
(define (cddaar l) (cdr (cdr (car (car l)))))
(define (cddadr l) (cdr (cdr (car (cdr l)))))
(define (cdddar l) (cdr (cdr (cdr (car l)))))
(define (cddddr l) (cdr (cdr (cdr (cdr l)))))
